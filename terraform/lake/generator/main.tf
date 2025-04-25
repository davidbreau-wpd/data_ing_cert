################################################################################
#                           BASE RESOURCES ☁️🔒
################################################################################

# ☁️ Provider Azure
provider "azurerm" {
  features {}
  subscription_id = var.subscription_id
}

# 👤 Provider AzureAD
provider "azuread" {}

# 🔍 Infos client actuel
data "azurerm_client_config" "current" {}

# 🌊 Compte de stockage Data Lake
resource "azurerm_storage_account" "adls" {
  name                     = var.adls_name
  resource_group_name      = var.resource_group_name
  location                 = var.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  account_kind             = "StorageV2"
  is_hns_enabled           = true
}

# 📦 Conteneur de stockage
resource "azurerm_storage_container" "container" {
  name                  = var.container_name
  storage_account_id    = azurerm_storage_account.adls.id
  container_access_type = "private"
}

# 🔒 Key Vault
resource "azurerm_key_vault" "kv" {
  name                        = var.kv_name
  location                    = var.location
  resource_group_name         = var.resource_group_name
  enabled_for_disk_encryption = true
  tenant_id                   = data.azurerm_client_config.current.tenant_id
  soft_delete_retention_days  = 7
  purge_protection_enabled    = false
  sku_name                    = "standard"
  
  # 🔐 Politique d'accès pour l'utilisateur actuel
  access_policy {
    tenant_id = data.azurerm_client_config.current.tenant_id
    object_id = data.azurerm_client_config.current.object_id
    
    secret_permissions = [
      "Get", "List", "Set", "Delete", "Purge"
    ]
  }
  
  # 🔐 Politique d'accès pour le Service Principal Key Vault
  access_policy {
    tenant_id = data.azurerm_client_config.current.tenant_id
    object_id = azuread_service_principal.sp_keyvault.object_id
    
    secret_permissions = [
      "Get", "List"
    ]
  }
}

################################################################################
#                        SERVICE PRINCIPALS & SECURITY 🛡️
################################################################################

# 📱 Application Azure AD pour Data Lake
resource "azuread_application" "app_datalake" {
  display_name = var.sp_name_1
  owners       = [data.azurerm_client_config.current.object_id]
}

# 🤖 Service Principal pour Data Lake
resource "azuread_service_principal" "sp_datalake" {
  client_id    = azuread_application.app_datalake.client_id
  owners       = [data.azurerm_client_config.current.object_id]
}

# 🔑 Mot de passe pour le SP Data Lake
resource "azuread_service_principal_password" "sp_datalake_password" {
  service_principal_id = azuread_service_principal.sp_datalake.id
  end_date             = "2099-01-01T00:00:00Z"
}

# 📱 Application Azure AD pour Key Vault
resource "azuread_application" "app_keyvault" {
  display_name = var.sp_name_2
  owners       = [data.azurerm_client_config.current.object_id]
}

# 🤖 Service Principal pour Key Vault
resource "azuread_service_principal" "sp_keyvault" {
  client_id    = azuread_application.app_keyvault.client_id
  owners       = [data.azurerm_client_config.current.object_id]
}

# 🔑 Mot de passe pour le SP Key Vault
resource "azuread_service_principal_password" "sp_keyvault_password" {
  service_principal_id = azuread_service_principal.sp_keyvault.id
  end_date             = "2099-01-01T00:00:00Z"
}



# 🔐 Stockage du mot de passe du SP Data Lake dans Key Vault
resource "azurerm_key_vault_secret" "sp_datalake_password" {
  name         = "sp-datalake-password"
  value        = azuread_service_principal_password.sp_datalake_password.value
  key_vault_id = azurerm_key_vault.kv.id
}

# 👮 Attribution de rôle pour le Service Principal sur le Data Lake
resource "azurerm_role_assignment" "sp_role" {
  scope                = azurerm_storage_account.adls.id
  role_definition_name = var.sp_role_1
  principal_id         = azuread_service_principal.sp_datalake.object_id
}

################################################################################
#                              FOLDERS 📁
################################################################################

locals {
  folders = [
    "enercon/input",
    "enercon/output/metadatas",
    "enercon/output/inspection_checklists",
    "vestas/input",
    "vestas/output/metadatas",
    "vestas/output/inspection_checklists"
  ]
}
resource "azurerm_storage_data_lake_gen2_path" "folders" {
  for_each           = toset(local.folders)
  path               = each.value
  filesystem_name    = azurerm_storage_container.container.name
  storage_account_id = azurerm_storage_account.adls.id
  resource           = "directory"
}
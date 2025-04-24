################################################################################
#                        SERVICE PRINCIPALS & SECURITY OUTPUTS 🛡️
################################################################################

# 🔑 ID du Service Principal Data Lake
output "sp_datalake_id" {
  value       = azuread_service_principal.sp_datalake.client_id
  description = "ID du Service Principal Data Lake"
  sensitive   = true
}

# 🔐 Mot de passe du Service Principal Data Lake
output "sp_datalake_password" {
  value       = azuread_service_principal_password.sp_datalake_password.value
  description = "Mot de passe du Service Principal Data Lake"
  sensitive   = true
}

# 🏢 ID du tenant Azure
output "tenant_id" {
  value       = data.azurerm_client_config.current.tenant_id
  description = "ID du tenant Azure"
  sensitive   = true
}

# 🔑 ID du Service Principal Key Vault
output "sp_keyvault_id" {
  value       = azuread_service_principal.sp_keyvault.client_id
  description = "ID du Service Principal Key Vault"
  sensitive   = true
}

# 🔐 Mot de passe du Service Principal Key Vault
output "sp_keyvault_password" {
  value       = azuread_service_principal_password.sp_keyvault_password.value
  description = "Mot de passe du Service Principal Key Vault"
  sensitive   = true
}
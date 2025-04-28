# Variables pour le déploiement Terraform
# Basées sur votre fichier variables.sh

# 📂 RESOURCE GROUP
variable "resource_group_name" {
  description = "Name of the existing Azure resource group"
  default     = "RG_DBREAU"
}

# 📍 LOCATION
variable "location" {
  description = "Azure resources location"
  default     = "francecentral"
}

# 🌊 DATA LAKE
variable "adls_name" {
  description = "Name of the Data Lake storage account"
  default     = "wpdwindmanagerfradls"
}

# 📦 CONTAINER
variable "container_name" {
  description = "Name of the storage container"
  default     = "service-reports"
}

# 🆔 SERVICE PRINCIPAL - DATA LAKE
variable "sp_name_1" {
  description = "Name of the Service Principal for Data Lake"
  default     = "sp_adls"
}

# 🔑 ROLE
variable "sp_role_1" {
  description = "Role of the Service Principal for Data Lake"
  default     = "Storage Blob Data Contributor"
}

# 🆔 SERVICE PRINCIPAL - KEYVAULT
variable "sp_name_2" {
  description = "Name of the Service Principal for Key Vault"
  default     = "sp_keyvault"
}

# 🔒 KEYVAULT
variable "kv_name" {
  description = "Name of the Key Vault"
  default     = "wpd-windmanager-fr-kv"
}

# 🔐 SECRET
variable "kv_secret_name" {
  description = "Name of the secret in Key Vault"
  default     = "sp-keyvault-dbreau-password"
}

# 💠 AZURE SUBSCRIPTION ID
variable "subscription_id" {
  description = "Azure subscription ID"
  default     = "029b3537-0f24-400b-b624-6058a145efe1"
}

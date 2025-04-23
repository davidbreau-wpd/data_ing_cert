# Variables pour le déploiement Terraform
# Basées sur votre fichier variables.sh

# 📂 RESOURCE GROUP
variable "resource_group_name" {
  description = "Nom du groupe de ressources existant"
  default     = "RG_DBREAU"
}

# 📍 LOCATION
variable "location" {
  description = "Localisation des ressources Azure"
  default     = "francecentral"
}

# 🌊 DATA LAKE
variable "adls_name" {
  description = "Nom du compte de stockage Data Lake"
  default     = "wpdwindmanagerfradls"
}

# 📦 CONTAINER
variable "container_name" {
  description = "Nom du conteneur"
  default     = "service-reports"
}

# 🆔 SERVICE PRINCIPAL - DATA LAKE
variable "sp_name_1" {
  description = "Nom du Service Principal pour Data Lake"
  default     = "sp_adls"
}

# 🔑 ROLE
variable "sp_role_1" {
  description = "Rôle du Service Principal pour Data Lake"
  default     = "Storage Blob Data Contributor"
}

# 🆔 SERVICE PRINCIPAL - KEYVAULT
variable "sp_name_2" {
  description = "Nom du Service Principal pour Key Vault"
  default     = "sp_keyvault"
}

# 🔒 KEYVAULT
variable "kv_name" {
  description = "Nom du Key Vault"
  default     = "wpd-windmanager-fr-kv"
}

# 🔐 SECRET
variable "kv_secret_name" {
  description = "Nom du secret dans Key Vault"
  default     = "sp-keyvault-dbreau-password"
}

# 💠 IDde l'abonnement Azure
variable "subscription_id" {
  description = "ID de l'abonnement Azure"
  default     = "029b3537-0f24-400b-b624-6058a145efe1"  # ID fourni
}

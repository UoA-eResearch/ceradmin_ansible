variable "os_application_credential_id" {
  description = "The application credential ID"
  type        = string
  default     = null
}

variable "os_application_credential_secret" {
  description = "The application credential secret"
  type        = string
  default     = null
}

variable "os_auth_url" {
  description = "The identity authentication URL"
  type        = string
  default     = null
}

variable "os_region" {
  description = "The region to use for the instance"
  type        = string
  default     = null

}

variable "os_project_id" {
  description = "The target project ID"
  type        = string
  default     = null
}

variable "os_project_name" {
  description = "The target project name"
  type        = string
  default     = null
}

variable "os_availability_zone" {
  description = "The availability zone to use for the instance"
  type        = string
  default     = null
}

variable "os_image_id" {
  description = "The ID of the image to use for the instance"
  type        = string
  default     = null
}

variable "os_flavor_id" {
  description = "The ID of the flavor to use for the instance"
  type        = string
  default     = null
}

variable "os_dns_zone" {
  description = "The DNS zone ID to use for the instance"
  type        = string
  default     = null
}

variable "username" {
  description = "The user name"
  type        = string
  default     = null
}

variable "password" {
  description = "The password"
  type        = string
  default     = null
}

variable "auth_url" {
  description = "The identity authentication URL"
  type        = string
  default     = null
}

variable "region" {
  description = "The region to use for the instance"
  type        = string
  default     = null

}

variable "project_id" {
  description = "The target project ID"
  type        = string
  default     = null
}

variable "project_name" {
  description = "The target project name"
  type        = string
  default     = null
}

variable "availability_zone" {
  description = "The availability zone to use for the instance"
  type        = string
  default     = null
}

variable "image_id" {
  description = "The ID of the image to use for the instance"
  type        = string
  default     = null
}

variable "flavor_id" {
  description = "The ID of the flavor to use for the instance"
  type        = string
  default     = null
}

variable "dns_zone" {
  description = "The DNS zone ID to use for the instance"
  type        = string
  default     = null
}

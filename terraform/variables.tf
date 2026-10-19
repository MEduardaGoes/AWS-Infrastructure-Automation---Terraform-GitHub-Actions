variable "project_name" {
  description = "Project identifier used in resource names and tags: 3-40 lowercase letters, digits, or single hyphens, starting with a letter."
  type        = string
  default     = "aws-terraform-cicd-pipeline"
  nullable    = false

  validation {
    condition = (
      length(var.project_name) >= 3 &&
      length(var.project_name) <= 40 &&
      can(regex("^[a-z][a-z0-9]*(-[a-z0-9]+)*$", var.project_name))
    )
    error_message = "project_name must be 3-40 lowercase letters, digits, or single hyphens, start with a letter, and end with a letter or digit."
  }
}

variable "environment" {
  description = "Deployment environment used in resource names and tags: dev, staging, or prod."
  type        = string
  default     = "dev"
  nullable    = false

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "environment must be dev, staging, or prod."
  }
}

variable "aws_region" {
  description = "AWS region for future resources. Validation checks region format; availability and account access are checked by AWS later."
  type        = string
  default     = "us-east-1"
  nullable    = false

  validation {
    condition     = can(regex("^[a-z]{2}(-[a-z]+)+-[0-9]+$", var.aws_region))
    error_message = "aws_region must use an AWS region format such as us-east-1 or sa-east-1."
  }
}

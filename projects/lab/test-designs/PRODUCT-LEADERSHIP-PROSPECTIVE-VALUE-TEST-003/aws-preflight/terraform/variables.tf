variable "aws_account_id" {
  description = "Twelve-digit isolated non-production AWS account ID fixed by a future authorization."
  type        = string

  validation {
    condition     = can(regex("^[0-9]{12}$", var.aws_account_id))
    error_message = "aws_account_id must contain exactly 12 digits."
  }
}

variable "aws_region" {
  description = "Single AWS region fixed by a future authorization."
  type        = string

  validation {
    condition     = can(regex("^[a-z]{2}(-gov)?-[a-z]+-[0-9]$", var.aws_region))
    error_message = "aws_region must be a valid fixed AWS region identifier."
  }
}

variable "name_suffix" {
  description = "Globally unique, non-sensitive suffix for disposable bucket names."
  type        = string

  validation {
    condition     = can(regex("^[a-z0-9][a-z0-9-]{2,20}$", var.name_suffix))
    error_message = "name_suffix must be 3-21 lowercase alphanumeric/hyphen characters."
  }
}

variable "governance_retention_days" {
  description = "Short explicit Object Lock Governance retention period fixed by future authorization."
  type        = number
  default     = 7

  validation {
    condition     = var.governance_retention_days >= 1 && var.governance_retention_days <= 30
    error_message = "Disposable preflight retention must be between 1 and 30 days."
  }
}

variable "codex_task_principal_arns" {
  description = "Six distinct external principals allowed to assume exactly one Codex task role each."
  type        = map(string)
  sensitive   = true

  validation {
    condition = length(var.codex_task_principal_arns) == 6 && alltrue([
      for role_key in ["package-generator", "baseline-generator", "normalization-operator", "evaluator-1", "evaluator-2", "evaluator-3"] :
      contains(keys(var.codex_task_principal_arns), role_key)
    ]) && length(toset(values(var.codex_task_principal_arns))) == 6
    error_message = "Exactly six distinct Codex task principal ARNs are required."
  }
}

variable "codex_task_external_ids" {
  description = "Six distinct external IDs bound one-to-one to Codex task roles."
  type        = map(string)
  sensitive   = true

  validation {
    condition = length(var.codex_task_external_ids) == 6 && alltrue([
      for role_key in ["package-generator", "baseline-generator", "normalization-operator", "evaluator-1", "evaluator-2", "evaluator-3"] :
      contains(keys(var.codex_task_external_ids), role_key)
    ]) && length(toset(values(var.codex_task_external_ids))) == 6
    error_message = "Exactly six distinct Codex task external IDs are required."
  }
}

variable "custodian_principal_arn" {
  description = "External non-Codex custodian principal ARN."
  type        = string
  sensitive   = true
}

variable "custodian_external_id" {
  description = "External ID known only to the future custodian assignment workflow."
  type        = string
  sensitive   = true
}

variable "claude_auditor_principal_arn" {
  description = "External Claude auditor principal ARN."
  type        = string
  sensitive   = true
}

variable "claude_auditor_external_id" {
  description = "External ID for the independent Claude auditor trust."
  type        = string
  sensitive   = true
}

variable "controller_principal_arn" {
  description = "Bounded administrative bootstrap principal ARN; MFA is mandatory."
  type        = string
  sensitive   = true
}

variable "controller_external_id" {
  description = "External ID for the bounded controller trust."
  type        = string
  sensitive   = true
}

variable "kms_administrator_principal_arn" {
  description = "Dedicated key administrator principal, separate from all key-use roles."
  type        = string
  sensitive   = true
}

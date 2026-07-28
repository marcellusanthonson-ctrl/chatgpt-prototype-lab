locals {
  prefix = "pl003-preflight"

  mandatory_tags = {
    Project     = "PRODUCT-LEADERSHIP-TEST-003"
    Environment = "PREFLIGHT"
    DataClass   = "SYNTHETIC-NON-TEST"
    Owner       = "LAB"
    Disposable  = "true"
    ManagedBy   = "Terraform"
  }

  codex_roles = {
    package-generator = {
      read_prefixes  = ["inputs"]
      write_prefixes = ["package-generator"]
    }
    baseline-generator = {
      read_prefixes  = ["inputs"]
      write_prefixes = ["baseline-generator"]
    }
    normalization-operator = {
      read_prefixes  = ["frozen-raw"]
      write_prefixes = ["normalized"]
    }
    evaluator-1 = {
      read_prefixes  = ["blinded"]
      write_prefixes = ["evaluations/evaluator-1"]
    }
    evaluator-2 = {
      read_prefixes  = ["blinded"]
      write_prefixes = ["evaluations/evaluator-2"]
    }
    evaluator-3 = {
      read_prefixes  = ["blinded"]
      write_prefixes = ["evaluations/evaluator-3"]
    }
  }

  role_names = concat(
    [for role_key in keys(local.codex_roles) : "${local.prefix}-${role_key}"],
    [
      "${local.prefix}-randomization-custodian",
      "${local.prefix}-claude-auditor",
      "${local.prefix}-controller"
    ]
  )

  role_arns = {
    for role_name in local.role_names :
    role_name => "arn:aws:iam::${var.aws_account_id}:role/${role_name}"
  }

  all_subject_role_arns = values(local.role_arns)

  bucket_names = {
    artifacts = "${local.prefix}-artifacts-${var.aws_account_id}-${var.name_suffix}"
    audit     = "${local.prefix}-audit-${var.aws_account_id}-${var.name_suffix}"
    custody   = "${local.prefix}-custody-${var.aws_account_id}-${var.name_suffix}"
  }
}

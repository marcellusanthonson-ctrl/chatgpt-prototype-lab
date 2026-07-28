resource "aws_kms_key" "artifacts" {
  description             = "PL003 disposable preflight artifact encryption"
  deletion_window_in_days = 7
  enable_key_rotation     = true

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "KeyAdministrationOnly"
        Effect    = "Allow"
        Principal = { AWS = var.kms_administrator_principal_arn }
        Action = [
          "kms:CancelKeyDeletion",
          "kms:CreateAlias",
          "kms:DeleteAlias",
          "kms:DescribeKey",
          "kms:DisableKey",
          "kms:EnableKey",
          "kms:EnableKeyRotation",
          "kms:GetKeyPolicy",
          "kms:GetKeyRotationStatus",
          "kms:ListResourceTags",
          "kms:PutKeyPolicy",
          "kms:ScheduleKeyDeletion",
          "kms:TagResource",
          "kms:UntagResource",
          "kms:UpdateAlias",
          "kms:UpdateKeyDescription"
        ]
        Resource = "*"
      },
      {
        Sid    = "ArtifactKeyUseByScopedRoles"
        Effect = "Allow"
        Principal = {
          AWS = concat(
            [for role_key in keys(local.codex_roles) : local.role_arns["${local.prefix}-${role_key}"]],
            [
              local.role_arns["${local.prefix}-claude-auditor"],
              local.role_arns["${local.prefix}-controller"]
            ]
          )
        }
        Action = [
          "kms:Decrypt",
          "kms:DescribeKey",
          "kms:Encrypt",
          "kms:GenerateDataKey"
        ]
        Resource = "*"
        Condition = {
          StringEquals = {
            "kms:ViaService"    = "s3.${var.aws_region}.amazonaws.com"
            "kms:CallerAccount" = var.aws_account_id
          }
        }
      }
    ]
  })
}

resource "aws_kms_alias" "artifacts" {
  name          = "alias/${local.prefix}-artifacts"
  target_key_id = aws_kms_key.artifacts.key_id
}

resource "aws_kms_key" "audit" {
  description             = "PL003 disposable preflight immutable audit encryption"
  deletion_window_in_days = 7
  enable_key_rotation     = true

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "KeyAdministrationOnly"
        Effect    = "Allow"
        Principal = { AWS = var.kms_administrator_principal_arn }
        Action = [
          "kms:CancelKeyDeletion",
          "kms:CreateAlias",
          "kms:DeleteAlias",
          "kms:DescribeKey",
          "kms:DisableKey",
          "kms:EnableKey",
          "kms:EnableKeyRotation",
          "kms:GetKeyPolicy",
          "kms:GetKeyRotationStatus",
          "kms:ListResourceTags",
          "kms:PutKeyPolicy",
          "kms:ScheduleKeyDeletion",
          "kms:TagResource",
          "kms:UntagResource",
          "kms:UpdateAlias",
          "kms:UpdateKeyDescription"
        ]
        Resource = "*"
      },
      {
        Sid       = "CloudTrailEncryptOnly"
        Effect    = "Allow"
        Principal = { Service = "cloudtrail.amazonaws.com" }
        Action    = ["kms:DescribeKey", "kms:GenerateDataKey"]
        Resource  = "*"
        Condition = {
          StringEquals = {
            "aws:SourceArn" = "arn:aws:cloudtrail:${var.aws_region}:${var.aws_account_id}:trail/${local.prefix}-trail"
          }
          StringLike = {
            "kms:EncryptionContext:aws:cloudtrail:arn" = "arn:aws:cloudtrail:*:${var.aws_account_id}:trail/*"
          }
        }
      },
      {
        Sid    = "AuditReadByAuditorAndController"
        Effect = "Allow"
        Principal = {
          AWS = [
            local.role_arns["${local.prefix}-claude-auditor"],
            local.role_arns["${local.prefix}-controller"]
          ]
        }
        Action = [
          "kms:Decrypt",
          "kms:DescribeKey"
        ]
        Resource = "*"
        Condition = {
          StringEquals = {
            "kms:ViaService"    = "s3.${var.aws_region}.amazonaws.com"
            "kms:CallerAccount" = var.aws_account_id
          }
        }
      }
    ]
  })
}

resource "aws_kms_alias" "audit" {
  name          = "alias/${local.prefix}-audit"
  target_key_id = aws_kms_key.audit.key_id
}

resource "aws_kms_key" "custody" {
  description             = "PL003 disposable preflight custodian-exclusive encryption"
  deletion_window_in_days = 7
  enable_key_rotation     = true

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "KeyAdministrationWithoutKeyUse"
        Effect    = "Allow"
        Principal = { AWS = var.kms_administrator_principal_arn }
        Action = [
          "kms:CancelKeyDeletion",
          "kms:CreateAlias",
          "kms:DeleteAlias",
          "kms:DescribeKey",
          "kms:DisableKey",
          "kms:EnableKey",
          "kms:EnableKeyRotation",
          "kms:GetKeyPolicy",
          "kms:GetKeyRotationStatus",
          "kms:ListResourceTags",
          "kms:PutKeyPolicy",
          "kms:ScheduleKeyDeletion",
          "kms:TagResource",
          "kms:UntagResource",
          "kms:UpdateAlias",
          "kms:UpdateKeyDescription"
        ]
        Resource = "*"
      },
      {
        Sid       = "CustodianExclusiveKeyUse"
        Effect    = "Allow"
        Principal = { AWS = local.role_arns["${local.prefix}-randomization-custodian"] }
        Action = [
          "kms:Decrypt",
          "kms:DescribeKey",
          "kms:Encrypt",
          "kms:GenerateDataKey"
        ]
        Resource = "*"
        Condition = {
          StringEquals = {
            "kms:CallerAccount" = var.aws_account_id
          }
        }
      },
      {
        Sid          = "DenyDecryptToEveryNonCustodianSubjectRole"
        Effect       = "Deny"
        NotPrincipal = { AWS = local.role_arns["${local.prefix}-randomization-custodian"] }
        Action       = "kms:Decrypt"
        Resource     = "*"
      }
    ]
  })
}

resource "aws_kms_alias" "custody" {
  name          = "alias/${local.prefix}-custodian"
  target_key_id = aws_kms_key.custody.key_id
}

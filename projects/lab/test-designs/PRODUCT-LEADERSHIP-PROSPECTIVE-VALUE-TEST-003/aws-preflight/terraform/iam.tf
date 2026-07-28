resource "aws_iam_policy" "subject_boundary" {
  name        = "${local.prefix}-subject-boundary"
  description = "Maximum data-plane permissions and immutable control-plane denies for all nine PL003 preflight roles."

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "BoundedDataPlaneMaximum"
        Effect = "Allow"
        Action = [
          "cloudtrail:GetTrailStatus",
          "kms:Decrypt",
          "kms:DescribeKey",
          "kms:Encrypt",
          "kms:GenerateDataKey",
          "s3:GetBucketLocation",
          "s3:GetObject",
          "s3:GetObjectRetention",
          "s3:GetObjectVersion",
          "s3:ListBucket",
          "s3:ListBucketVersions",
          "s3:PutObject",
          "secretsmanager:DescribeSecret",
          "secretsmanager:GetSecretValue",
          "secretsmanager:PutSecretValue"
        ]
        Resource = concat(
          [
            aws_s3_bucket.buckets["artifacts"].arn,
            "${aws_s3_bucket.buckets["artifacts"].arn}/*",
            aws_s3_bucket.buckets["audit"].arn,
            "${aws_s3_bucket.buckets["audit"].arn}/*",
            aws_s3_bucket.buckets["custody"].arn,
            "${aws_s3_bucket.buckets["custody"].arn}/*",
            aws_kms_key.artifacts.arn,
            aws_kms_key.audit.arn,
            aws_kms_key.custody.arn,
            aws_secretsmanager_secret.custody.arn,
            "arn:aws:cloudtrail:${var.aws_region}:${var.aws_account_id}:trail/${local.prefix}-trail"
          ]
        )
      },
      {
        Sid    = "DenyControlPlaneMutation"
        Effect = "Deny"
        Action = [
          "cloudtrail:CreateTrail",
          "cloudtrail:DeleteTrail",
          "cloudtrail:PutEventSelectors",
          "cloudtrail:StartLogging",
          "cloudtrail:StopLogging",
          "cloudtrail:UpdateTrail",
          "iam:AttachRolePolicy",
          "iam:CreatePolicy",
          "iam:CreatePolicyVersion",
          "iam:CreateRole",
          "iam:DeletePolicy",
          "iam:DeletePolicyVersion",
          "iam:DeleteRole",
          "iam:DeleteRolePermissionsBoundary",
          "iam:DetachRolePolicy",
          "iam:PutRolePermissionsBoundary",
          "iam:PutRolePolicy",
          "iam:SetDefaultPolicyVersion",
          "iam:UpdateAssumeRolePolicy",
          "kms:CreateGrant",
          "kms:DisableKey",
          "kms:PutKeyPolicy",
          "kms:RetireGrant",
          "kms:RevokeGrant",
          "kms:ScheduleKeyDeletion",
          "s3:BypassGovernanceRetention",
          "s3:DeleteBucket",
          "s3:DeleteBucketPolicy",
          "s3:DeleteObject",
          "s3:DeleteObjectVersion",
          "s3:PutBucketAcl",
          "s3:PutBucketObjectLockConfiguration",
          "s3:PutBucketPolicy",
          "s3:PutBucketPublicAccessBlock",
          "s3:PutBucketVersioning",
          "s3:PutEncryptionConfiguration",
          "s3:PutObjectLegalHold",
          "s3:PutObjectRetention",
          "secretsmanager:DeleteResourcePolicy",
          "secretsmanager:DeleteSecret",
          "secretsmanager:PutResourcePolicy",
          "secretsmanager:UpdateSecret"
        ]
        Resource = "*"
      },
      {
        Sid      = "DenyIncompatibleRoleChaining"
        Effect   = "Deny"
        Action   = "sts:AssumeRole"
        Resource = local.all_subject_role_arns
      }
    ]
  })
}

resource "aws_iam_role" "codex" {
  for_each = local.codex_roles

  name                 = "${local.prefix}-${each.key}"
  max_session_duration = 3600
  permissions_boundary = aws_iam_policy.subject_boundary.arn

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Sid       = "DistinctExternalTaskTrust"
      Effect    = "Allow"
      Principal = { AWS = var.codex_task_principal_arns[each.key] }
      Action    = "sts:AssumeRole"
      Condition = {
        StringEquals = {
          "sts:ExternalId" = var.codex_task_external_ids[each.key]
        }
      }
    }]
  })
}

resource "aws_iam_role_policy" "codex" {
  for_each = local.codex_roles

  name = "${local.prefix}-${each.key}-minimum"
  role = aws_iam_role.codex[each.key].id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "ListOnlyAuthorizedPrefixes"
        Effect = "Allow"
        Action = [
          "s3:GetBucketLocation",
          "s3:ListBucket"
        ]
        Resource = aws_s3_bucket.buckets["artifacts"].arn
        Condition = {
          StringLike = {
            "s3:prefix" = concat(
              [for prefix in each.value.read_prefixes : "${prefix}/*"],
              [for prefix in each.value.write_prefixes : "${prefix}/*"]
            )
          }
        }
      },
      {
        Sid      = "ReadOnlyAuthorizedInputs"
        Effect   = "Allow"
        Action   = ["s3:GetObject", "s3:GetObjectVersion"]
        Resource = [for prefix in each.value.read_prefixes : "${aws_s3_bucket.buckets["artifacts"].arn}/${prefix}/*"]
      },
      {
        Sid      = "WriteOnlyOwnPrefix"
        Effect   = "Allow"
        Action   = "s3:PutObject"
        Resource = [for prefix in each.value.write_prefixes : "${aws_s3_bucket.buckets["artifacts"].arn}/${prefix}/*"]
        Condition = {
          StringEquals = {
            "s3:x-amz-server-side-encryption"                = "aws:kms"
            "s3:x-amz-server-side-encryption-aws-kms-key-id" = aws_kms_key.artifacts.arn
          }
        }
      },
      {
        Sid      = "ArtifactKeyUseThroughS3Only"
        Effect   = "Allow"
        Action   = ["kms:Decrypt", "kms:DescribeKey", "kms:Encrypt", "kms:GenerateDataKey"]
        Resource = aws_kms_key.artifacts.arn
        Condition = {
          StringEquals = {
            "kms:ViaService"    = "s3.${var.aws_region}.amazonaws.com"
            "kms:CallerAccount" = var.aws_account_id
          }
        }
      },
      {
        Sid    = "ExplicitDenyOtherSensitivePlanes"
        Effect = "Deny"
        Action = [
          "kms:Decrypt",
          "s3:GetObject",
          "s3:GetObjectVersion",
          "s3:PutObject",
          "secretsmanager:DescribeSecret",
          "secretsmanager:GetSecretValue",
          "secretsmanager:PutSecretValue"
        ]
        Resource = [
          aws_kms_key.custody.arn,
          aws_secretsmanager_secret.custody.arn,
          "${aws_s3_bucket.buckets["custody"].arn}/*"
        ]
      }
    ]
  })
}

resource "aws_iam_role" "custodian" {
  name                 = "${local.prefix}-randomization-custodian"
  max_session_duration = 3600
  permissions_boundary = aws_iam_policy.subject_boundary.arn

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Sid       = "ExternalCustodianOnly"
      Effect    = "Allow"
      Principal = { AWS = var.custodian_principal_arn }
      Action    = "sts:AssumeRole"
      Condition = {
        StringEquals = { "sts:ExternalId" = var.custodian_external_id }
      }
    }]
  })
}

resource "aws_iam_role_policy" "custodian" {
  name = "${local.prefix}-custodian-exclusive"
  role = aws_iam_role.custodian.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid      = "CustodianSecretOnly"
        Effect   = "Allow"
        Action   = ["secretsmanager:DescribeSecret", "secretsmanager:GetSecretValue", "secretsmanager:PutSecretValue"]
        Resource = aws_secretsmanager_secret.custody.arn
      },
      {
        Sid      = "CustodianKeyUseOnly"
        Effect   = "Allow"
        Action   = ["kms:Decrypt", "kms:DescribeKey", "kms:Encrypt", "kms:GenerateDataKey"]
        Resource = aws_kms_key.custody.arn
      },
      {
        Sid      = "CustodyBucketList"
        Effect   = "Allow"
        Action   = ["s3:GetBucketLocation", "s3:ListBucket"]
        Resource = aws_s3_bucket.buckets["custody"].arn
        Condition = {
          StringLike = {
            "s3:prefix" = [
              "encrypted-mapping/*",
              "custodian-attestations/*",
              "release-records/*"
            ]
          }
        }
      },
      {
        Sid    = "CustodyObjectsOnly"
        Effect = "Allow"
        Action = ["s3:GetObject", "s3:GetObjectVersion", "s3:PutObject"]
        Resource = [
          "${aws_s3_bucket.buckets["custody"].arn}/encrypted-mapping/*",
          "${aws_s3_bucket.buckets["custody"].arn}/custodian-attestations/*",
          "${aws_s3_bucket.buckets["custody"].arn}/release-records/*"
        ]
      },
      {
        Sid    = "ExplicitDenyArtifactAndAuditMutation"
        Effect = "Deny"
        Action = "s3:PutObject"
        Resource = [
          "${aws_s3_bucket.buckets["artifacts"].arn}/*",
          "${aws_s3_bucket.buckets["audit"].arn}/*"
        ]
      }
    ]
  })
}

resource "aws_iam_role" "auditor" {
  name                 = "${local.prefix}-claude-auditor"
  max_session_duration = 3600
  permissions_boundary = aws_iam_policy.subject_boundary.arn

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Sid       = "ExternalClaudeReadOnlyTrust"
      Effect    = "Allow"
      Principal = { AWS = var.claude_auditor_principal_arn }
      Action    = "sts:AssumeRole"
      Condition = {
        StringEquals = { "sts:ExternalId" = var.claude_auditor_external_id }
      }
    }]
  })
}

resource "aws_iam_role_policy" "auditor" {
  name = "${local.prefix}-claude-read-only"
  role = aws_iam_role.auditor.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid      = "ReadReleasedFinalOnly"
        Effect   = "Allow"
        Action   = ["s3:GetObject", "s3:GetObjectVersion"]
        Resource = "${aws_s3_bucket.buckets["artifacts"].arn}/released-final/*"
      },
      {
        Sid    = "ReadReleasedAuditEvidence"
        Effect = "Allow"
        Action = ["s3:GetObject", "s3:GetObjectRetention", "s3:GetObjectVersion"]
        Resource = [
          "${aws_s3_bucket.buckets["audit"].arn}/access-evidence/*",
          "${aws_s3_bucket.buckets["audit"].arn}/deny-test-results/*",
          "${aws_s3_bucket.buckets["audit"].arn}/hash-manifests/*",
          "${aws_s3_bucket.buckets["audit"].arn}/checkpoint-attestations/*",
          "${aws_s3_bucket.buckets["audit"].arn}/preflight-report/*"
        ]
      },
      {
        Sid      = "ReadAuditAndArtifactKeysThroughS3"
        Effect   = "Allow"
        Action   = ["kms:Decrypt", "kms:DescribeKey"]
        Resource = [aws_kms_key.artifacts.arn, aws_kms_key.audit.arn]
        Condition = {
          StringEquals = {
            "kms:ViaService"    = "s3.${var.aws_region}.amazonaws.com"
            "kms:CallerAccount" = var.aws_account_id
          }
        }
      },
      {
        Sid    = "ExplicitReadOnlyAndNoUnreleasedAccess"
        Effect = "Deny"
        Action = [
          "kms:Decrypt",
          "s3:DeleteObject",
          "s3:DeleteObjectVersion",
          "s3:GetObject",
          "s3:GetObjectVersion",
          "s3:PutObject",
          "secretsmanager:GetSecretValue",
          "secretsmanager:PutSecretValue"
        ]
        Resource = [
          aws_kms_key.custody.arn,
          aws_secretsmanager_secret.custody.arn,
          "${aws_s3_bucket.buckets["custody"].arn}/*",
          "${aws_s3_bucket.buckets["artifacts"].arn}/inputs/*",
          "${aws_s3_bucket.buckets["artifacts"].arn}/package-generator/*",
          "${aws_s3_bucket.buckets["artifacts"].arn}/baseline-generator/*",
          "${aws_s3_bucket.buckets["artifacts"].arn}/frozen-raw/*",
          "${aws_s3_bucket.buckets["artifacts"].arn}/normalized/*",
          "${aws_s3_bucket.buckets["artifacts"].arn}/blinded/*",
          "${aws_s3_bucket.buckets["artifacts"].arn}/evaluations/*"
        ]
      }
    ]
  })
}

resource "aws_iam_role" "controller" {
  name                 = "${local.prefix}-controller"
  max_session_duration = 3600
  permissions_boundary = aws_iam_policy.subject_boundary.arn

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Sid       = "MfaBoundedControllerTrust"
      Effect    = "Allow"
      Principal = { AWS = var.controller_principal_arn }
      Action    = "sts:AssumeRole"
      Condition = {
        Bool         = { "aws:MultiFactorAuthPresent" = "true" }
        StringEquals = { "sts:ExternalId" = var.controller_external_id }
      }
    }]
  })
}

resource "aws_iam_role_policy" "controller" {
  name = "${local.prefix}-controller-verification-only"
  role = aws_iam_role.controller.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid      = "VerifyTrailStatus"
        Effect   = "Allow"
        Action   = "cloudtrail:GetTrailStatus"
        Resource = "arn:aws:cloudtrail:${var.aws_region}:${var.aws_account_id}:trail/${local.prefix}-trail"
      },
      {
        Sid      = "ReadPreflightEvidence"
        Effect   = "Allow"
        Action   = ["s3:GetObject", "s3:GetObjectRetention", "s3:GetObjectVersion"]
        Resource = "${aws_s3_bucket.buckets["audit"].arn}/preflight-report/*"
      },
      {
        Sid      = "AuditKeyReadThroughS3"
        Effect   = "Allow"
        Action   = ["kms:Decrypt", "kms:DescribeKey"]
        Resource = aws_kms_key.audit.arn
        Condition = {
          StringEquals = {
            "kms:ViaService"    = "s3.${var.aws_region}.amazonaws.com"
            "kms:CallerAccount" = var.aws_account_id
          }
        }
      },
      {
        Sid    = "ExplicitNoCustodianUse"
        Effect = "Deny"
        Action = [
          "kms:Decrypt",
          "s3:GetObject",
          "s3:GetObjectVersion",
          "s3:PutObject",
          "secretsmanager:GetSecretValue",
          "secretsmanager:PutSecretValue"
        ]
        Resource = [
          aws_kms_key.custody.arn,
          aws_secretsmanager_secret.custody.arn,
          "${aws_s3_bucket.buckets["custody"].arn}/*"
        ]
      }
    ]
  })
}

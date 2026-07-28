resource "aws_s3_bucket" "buckets" {
  for_each = local.bucket_names

  bucket              = each.value
  object_lock_enabled = true
  force_destroy       = false
}

resource "aws_s3_bucket_ownership_controls" "buckets" {
  for_each = aws_s3_bucket.buckets

  bucket = each.value.id

  rule {
    object_ownership = "BucketOwnerEnforced"
  }
}

resource "aws_s3_bucket_public_access_block" "buckets" {
  for_each = aws_s3_bucket.buckets

  bucket                  = each.value.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_versioning" "buckets" {
  for_each = aws_s3_bucket.buckets

  bucket = each.value.id

  versioning_configuration {
    status     = "Enabled"
    mfa_delete = "Disabled"
  }
}

resource "aws_s3_bucket_object_lock_configuration" "buckets" {
  for_each = aws_s3_bucket.buckets

  bucket = each.value.id

  rule {
    default_retention {
      mode = "GOVERNANCE"
      days = var.governance_retention_days
    }
  }

  depends_on = [aws_s3_bucket_versioning.buckets]
}

resource "aws_s3_bucket_server_side_encryption_configuration" "artifacts" {
  bucket = aws_s3_bucket.buckets["artifacts"].id

  rule {
    bucket_key_enabled = true
    apply_server_side_encryption_by_default {
      kms_master_key_id = aws_kms_key.artifacts.arn
      sse_algorithm     = "aws:kms"
    }
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "audit" {
  bucket = aws_s3_bucket.buckets["audit"].id

  rule {
    bucket_key_enabled = true
    apply_server_side_encryption_by_default {
      kms_master_key_id = aws_kms_key.audit.arn
      sse_algorithm     = "aws:kms"
    }
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "custody" {
  bucket = aws_s3_bucket.buckets["custody"].id

  rule {
    bucket_key_enabled = true
    apply_server_side_encryption_by_default {
      kms_master_key_id = aws_kms_key.custody.arn
      sse_algorithm     = "aws:kms"
    }
  }
}

resource "aws_s3_bucket_policy" "artifacts" {
  bucket = aws_s3_bucket.buckets["artifacts"].id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "DenyInsecureTransport"
        Effect    = "Deny"
        Principal = "*"
        Action    = "s3:*"
        Resource = [
          aws_s3_bucket.buckets["artifacts"].arn,
          "${aws_s3_bucket.buckets["artifacts"].arn}/*"
        ]
        Condition = { Bool = { "aws:SecureTransport" = "false" } }
      },
      {
        Sid       = "DenyFunctionalDeletionAndRetentionBypass"
        Effect    = "Deny"
        Principal = { AWS = local.all_subject_role_arns }
        Action = [
          "s3:BypassGovernanceRetention",
          "s3:DeleteObject",
          "s3:DeleteObjectVersion",
          "s3:PutBucketPolicy",
          "s3:PutObjectLegalHold",
          "s3:PutObjectRetention"
        ]
        Resource = [
          aws_s3_bucket.buckets["artifacts"].arn,
          "${aws_s3_bucket.buckets["artifacts"].arn}/*"
        ]
      }
    ]
  })
}

resource "aws_s3_bucket_policy" "custody" {
  bucket = aws_s3_bucket.buckets["custody"].id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "DenyInsecureTransport"
        Effect    = "Deny"
        Principal = "*"
        Action    = "s3:*"
        Resource = [
          aws_s3_bucket.buckets["custody"].arn,
          "${aws_s3_bucket.buckets["custody"].arn}/*"
        ]
        Condition = { Bool = { "aws:SecureTransport" = "false" } }
      },
      {
        Sid          = "DenyCustodyDataToNonCustodianSubjects"
        Effect       = "Deny"
        NotPrincipal = { AWS = local.role_arns["${local.prefix}-randomization-custodian"] }
        Action = [
          "s3:GetObject",
          "s3:GetObjectVersion",
          "s3:PutObject"
        ]
        Resource = "${aws_s3_bucket.buckets["custody"].arn}/*"
      },
      {
        Sid       = "DenyCustodyDeletionAndRetentionBypass"
        Effect    = "Deny"
        Principal = { AWS = local.all_subject_role_arns }
        Action = [
          "s3:BypassGovernanceRetention",
          "s3:DeleteObject",
          "s3:DeleteObjectVersion",
          "s3:PutBucketPolicy",
          "s3:PutObjectLegalHold",
          "s3:PutObjectRetention"
        ]
        Resource = [
          aws_s3_bucket.buckets["custody"].arn,
          "${aws_s3_bucket.buckets["custody"].arn}/*"
        ]
      }
    ]
  })
}

resource "aws_s3_bucket_policy" "audit" {
  bucket = aws_s3_bucket.buckets["audit"].id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "DenyInsecureTransport"
        Effect    = "Deny"
        Principal = "*"
        Action    = "s3:*"
        Resource = [
          aws_s3_bucket.buckets["audit"].arn,
          "${aws_s3_bucket.buckets["audit"].arn}/*"
        ]
        Condition = { Bool = { "aws:SecureTransport" = "false" } }
      },
      {
        Sid       = "CloudTrailAclCheck"
        Effect    = "Allow"
        Principal = { Service = "cloudtrail.amazonaws.com" }
        Action    = "s3:GetBucketAcl"
        Resource  = aws_s3_bucket.buckets["audit"].arn
        Condition = {
          StringEquals = {
            "aws:SourceArn" = "arn:aws:cloudtrail:${var.aws_region}:${var.aws_account_id}:trail/${local.prefix}-trail"
          }
        }
      },
      {
        Sid       = "CloudTrailWrite"
        Effect    = "Allow"
        Principal = { Service = "cloudtrail.amazonaws.com" }
        Action    = "s3:PutObject"
        Resource  = "${aws_s3_bucket.buckets["audit"].arn}/cloudtrail/AWSLogs/${var.aws_account_id}/*"
        Condition = {
          StringEquals = {
            "aws:SourceArn" = "arn:aws:cloudtrail:${var.aws_region}:${var.aws_account_id}:trail/${local.prefix}-trail"
            "s3:x-amz-acl"  = "bucket-owner-full-control"
          }
        }
      },
      {
        Sid       = "DenyAuditDeletionAndRetentionBypass"
        Effect    = "Deny"
        Principal = { AWS = local.all_subject_role_arns }
        Action = [
          "s3:BypassGovernanceRetention",
          "s3:DeleteObject",
          "s3:DeleteObjectVersion",
          "s3:PutBucketPolicy",
          "s3:PutObjectLegalHold",
          "s3:PutObjectRetention"
        ]
        Resource = [
          aws_s3_bucket.buckets["audit"].arn,
          "${aws_s3_bucket.buckets["audit"].arn}/*"
        ]
      }
    ]
  })
}

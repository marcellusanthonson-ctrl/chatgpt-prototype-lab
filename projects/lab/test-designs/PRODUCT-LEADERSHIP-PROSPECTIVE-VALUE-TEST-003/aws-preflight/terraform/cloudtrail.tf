resource "aws_cloudtrail" "preflight" {
  name                          = "${local.prefix}-trail"
  s3_bucket_name                = aws_s3_bucket.buckets["audit"].id
  s3_key_prefix                 = "cloudtrail"
  include_global_service_events = true
  is_multi_region_trail         = false
  enable_log_file_validation    = true
  enable_logging                = true
  kms_key_id                    = aws_kms_key.audit.arn

  advanced_event_selector {
    name = "AllManagementEvents"

    field_selector {
      field  = "eventCategory"
      equals = ["Management"]
    }
  }

  advanced_event_selector {
    name = "AllThreeBucketObjectDataEvents"

    field_selector {
      field  = "eventCategory"
      equals = ["Data"]
    }

    field_selector {
      field  = "resources.type"
      equals = ["AWS::S3::Object"]
    }

    field_selector {
      field = "resources.ARN"
      starts_with = [
        "${aws_s3_bucket.buckets["artifacts"].arn}/",
        "${aws_s3_bucket.buckets["audit"].arn}/",
        "${aws_s3_bucket.buckets["custody"].arn}/"
      ]
    }
  }

  depends_on = [
    aws_s3_bucket_policy.audit,
    aws_s3_bucket_object_lock_configuration.buckets,
    aws_s3_bucket_server_side_encryption_configuration.audit
  ]
}

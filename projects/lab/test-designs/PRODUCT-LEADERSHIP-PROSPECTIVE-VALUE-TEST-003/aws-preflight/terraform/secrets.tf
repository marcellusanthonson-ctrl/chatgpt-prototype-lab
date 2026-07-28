resource "aws_secretsmanager_secret" "custody" {
  name                    = "/pl003/preflight/randomization-mapping"
  description             = "Empty static container for a future authorized non-test synthetic sentinel only."
  kms_key_id              = aws_kms_key.custody.arn
  recovery_window_in_days = 7

  lifecycle {
    prevent_destroy = true
  }
}

# Intentionally no aws_secretsmanager_secret_version resource: this static package
# creates no secret value, sentinel, mapping, fixture, output, score, or oracle.
resource "aws_secretsmanager_secret_policy" "custody" {
  secret_arn          = aws_secretsmanager_secret.custody.arn
  block_public_policy = true

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "CustodianExclusiveSecretUse"
        Effect    = "Allow"
        Principal = { AWS = local.role_arns["${local.prefix}-randomization-custodian"] }
        Action = [
          "secretsmanager:DescribeSecret",
          "secretsmanager:GetSecretValue",
          "secretsmanager:PutSecretValue"
        ]
        Resource = aws_secretsmanager_secret.custody.arn
      },
      {
        Sid          = "DenyReadAndValueMutationToNonCustodian"
        Effect       = "Deny"
        NotPrincipal = { AWS = local.role_arns["${local.prefix}-randomization-custodian"] }
        Action = [
          "secretsmanager:GetSecretValue",
          "secretsmanager:PutSecretValue"
        ]
        Resource = aws_secretsmanager_secret.custody.arn
      }
    ]
  })
}

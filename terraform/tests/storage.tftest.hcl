mock_provider "aws" {
  override_during = plan

  mock_resource "aws_s3_bucket" {
    defaults = {
      id     = "offline-example-bucket"
      bucket = "offline-example-bucket"
      arn    = "arn:aws:s3:::offline-example-bucket"
    }
  }
}

run "secure_storage_defaults" {
  command = plan

  assert {
    condition     = aws_s3_bucket.example.force_destroy == false
    error_message = "Deleting the bucket must not automatically remove its objects."
  }

  assert {
    condition     = aws_s3_bucket_versioning.example.versioning_configuration[0].status == "Enabled"
    error_message = "Object versioning must be enabled."
  }

  assert {
    condition     = one(one(aws_s3_bucket_server_side_encryption_configuration.example.rule).apply_server_side_encryption_by_default).sse_algorithm == "AES256"
    error_message = "Default server-side encryption must use SSE-S3."
  }

  assert {
    condition = (
      aws_s3_bucket_public_access_block.example.block_public_acls &&
      aws_s3_bucket_public_access_block.example.block_public_policy &&
      aws_s3_bucket_public_access_block.example.ignore_public_acls &&
      aws_s3_bucket_public_access_block.example.restrict_public_buckets
    )
    error_message = "All four public access block controls must be enabled."
  }

  assert {
    condition = (
      length(jsondecode(aws_s3_bucket_policy.https_only.policy).Statement) == 1 &&
      jsondecode(aws_s3_bucket_policy.https_only.policy).Statement[0].Effect == "Deny" &&
      jsondecode(aws_s3_bucket_policy.https_only.policy).Statement[0].Principal == "*" &&
      jsondecode(aws_s3_bucket_policy.https_only.policy).Statement[0].Action == "s3:*" &&
      jsondecode(aws_s3_bucket_policy.https_only.policy).Statement[0].Condition.Bool["aws:SecureTransport"] == "false" &&
      contains(jsondecode(aws_s3_bucket_policy.https_only.policy).Statement[0].Resource, aws_s3_bucket.example.arn) &&
      contains(jsondecode(aws_s3_bucket_policy.https_only.policy).Statement[0].Resource, "${aws_s3_bucket.example.arn}/*")
    )
    error_message = "The policy must deny insecure transport for the bucket and its objects."
  }
}

run "custom_configuration" {
  command = plan

  variables {
    project_name = "portfolio-demo"
    environment  = "staging"
    aws_region   = "sa-east-1"
  }

  assert {
    condition     = aws_s3_bucket.example.bucket_prefix == "portfolio-demo-staging-"
    error_message = "The bucket prefix must reflect the project and environment."
  }
}

run "reject_invalid_project_name" {
  command = plan

  variables {
    project_name = "INVALID NAME"
  }

  expect_failures = [var.project_name]
}

run "reject_invalid_environment" {
  command = plan

  variables {
    environment = "production"
  }

  expect_failures = [var.environment]
}

run "reject_invalid_region_format" {
  command = plan

  variables {
    aws_region = "invalid"
  }

  expect_failures = [var.aws_region]
}

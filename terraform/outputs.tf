output "bucket_name" {
  description = "Name of the example storage bucket; mocked during offline tests."
  value       = aws_s3_bucket.example.bucket
}

output "bucket_arn" {
  description = "ARN of the example storage bucket; mocked during offline tests."
  value       = aws_s3_bucket.example.arn
}

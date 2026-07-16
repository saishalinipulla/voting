output "bucket_name" {
  value = aws_s3_bucket.voting_bucket.bucket
}

output "bucket_arn" {
  value = aws_s3_bucket.voting_bucket.arn
}

output "sns_topic_arn" {
  value = aws_sns_topic.voting_alerts.arn
}
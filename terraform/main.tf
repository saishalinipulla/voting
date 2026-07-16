resource "aws_s3_bucket" "voting_bucket" {
  bucket = var.bucket_name

  tags = {
    Name    = "Voting App Bucket"
    Project = "Voting App"
  }
}

resource "aws_sns_topic" "voting_alerts" {
  name = "voting-alerts-terraform"

  tags = {
    Name    = "Voting Alerts"
    Project = "Voting App"
  }
}
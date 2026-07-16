resource "aws_s3_bucket" "voting_bucket" {
  bucket = var.bucket_name

  tags = {
    Name    = "Voting App Bucket"
    Project = "Voting App"
  }
}
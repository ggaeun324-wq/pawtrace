# S3 — 신고/강아지 이미지 (CloudFront OAC는 P3에서 추가)
resource "aws_s3_bucket" "images" {
  bucket = "${var.project}-images-${data.aws_caller_identity.current.account_id}"
}

resource "aws_s3_bucket_public_access_block" "images" {
  bucket                  = aws_s3_bucket.images.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

data "aws_caller_identity" "current" {}

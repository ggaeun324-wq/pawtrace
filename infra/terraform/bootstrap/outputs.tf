# apply 후 출력되는 값들 — GitHub Secrets/Variables 에 넣습니다.
output "deploy_role_arn" {
  description = "→ GitHub Secret: AWS_DEPLOY_ROLE_ARN"
  value       = aws_iam_role.deploy.arn
}

output "terraform_role_arn" {
  description = "→ GitHub Secret: AWS_TF_ROLE_ARN (인프라 파이프라인용)"
  value       = aws_iam_role.terraform.arn
}

output "ecr_repository_url" {
  description = "ECR 이미지 저장소 URL"
  value       = aws_ecr_repository.api.repository_url
}

output "tfstate_bucket" {
  description = "Terraform 원격 상태 S3 버킷"
  value       = aws_s3_bucket.tfstate.bucket
}

output "tflock_table" {
  description = "Terraform 상태 잠금 DynamoDB 테이블"
  value       = aws_dynamodb_table.tflock.name
}

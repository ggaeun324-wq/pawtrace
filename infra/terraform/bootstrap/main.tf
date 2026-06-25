# Bootstrap — 1회만 실행. (관리자 자격증명 필요)
# 목적: GitHub Actions 가 키 없이(OIDC) AWS 에 배포할 수 있도록
#   1) GitHub OIDC Provider
#   2) 배포용 IAM Role (이 리포에서만 assume 가능)
#   3) ECR 리포지토리 (이미지 저장소)
#   4) Terraform 원격 상태 저장용 S3 + DynamoDB 잠금
# 을 생성합니다.
terraform {
  required_version = ">= 1.6"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

data "aws_caller_identity" "current" {}

# ── 1) GitHub OIDC Provider ────────────────────────────────
# GitHub Actions 토큰을 신뢰하기 위한 OIDC 공급자.
resource "aws_iam_openid_connect_provider" "github" {
  url             = "https://token.actions.githubusercontent.com"
  client_id_list  = ["sts.amazonaws.com"]
  thumbprint_list = ["6938fd4d98bab03faadb97b34396831e3780aea1"]
}

# ── 2) 배포용 IAM Role (OIDC로 assume) ─────────────────────
data "aws_iam_policy_document" "assume" {
  statement {
    actions = ["sts:AssumeRoleWithWebIdentity"]
    effect  = "Allow"

    principals {
      type        = "Federated"
      identifiers = [aws_iam_openid_connect_provider.github.arn]
    }

    condition {
      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:aud"
      values   = ["sts.amazonaws.com"]
    }

    # 지정한 리포의 지정 브랜치에서만 assume 허용 (최소권한)
    condition {
      test     = "StringLike"
      variable = "token.actions.githubusercontent.com:sub"
      values   = ["repo:${var.github_repo}:ref:refs/heads/${var.github_branch}"]
    }
  }
}

resource "aws_iam_role" "deploy" {
  name               = "${var.project}-gha-deploy"
  assume_role_policy = data.aws_iam_policy_document.assume.json
}

# 배포에 필요한 권한 (ECR push + ECS 업데이트). 운영에서는 더 좁힐 수 있습니다.
resource "aws_iam_role_policy_attachment" "ecr" {
  role       = aws_iam_role.deploy.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryPowerUser"
}

resource "aws_iam_role_policy" "ecs_deploy" {
  name = "${var.project}-ecs-deploy"
  role = aws_iam_role.deploy.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ecs:UpdateService",
          "ecs:DescribeServices",
          "ecs:RegisterTaskDefinition",
          "ecs:DescribeTaskDefinition",
          "ecs:RunTask",
          "iam:PassRole"
        ]
        Resource = "*"
      }
    ]
  })
}

# ── 3) ECR 리포지토리 ──────────────────────────────────────
resource "aws_ecr_repository" "api" {
  name                 = "${var.project}-api"
  image_tag_mutability = "IMMUTABLE"
  image_scanning_configuration {
    scan_on_push = true
  }
}

# ── 4) Terraform 원격 상태 (S3 + DynamoDB 잠금) ────────────
resource "aws_s3_bucket" "tfstate" {
  bucket = "${var.project}-tfstate-${data.aws_caller_identity.current.account_id}"
}

resource "aws_s3_bucket_versioning" "tfstate" {
  bucket = aws_s3_bucket.tfstate.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_dynamodb_table" "tflock" {
  name         = "${var.project}-tflock"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "LockID"
  attribute {
    name = "LockID"
    type = "S"
  }
}

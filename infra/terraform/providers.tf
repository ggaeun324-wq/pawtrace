terraform {
  required_version = ">= 1.6"
  required_providers {
    aws    = { source = "hashicorp/aws", version = "~> 5.0" }
    random = { source = "hashicorp/random", version = "~> 3.0" }
  }

  # 원격 상태 (bootstrap 에서 만든 S3/DynamoDB).
  # GitHub Actions 와 로컬이 동일한 상태파일을 공유하기 위해 S3 백엔드를 사용합니다.
  # 주의: backend 블록은 변수를 쓸 수 없어 버킷명을 직접 적습니다(계정 ID 포함).
  backend "s3" {
    bucket         = "pawtrace-tfstate-545750751672"
    key            = "main/terraform.tfstate"
    region         = "ap-northeast-2"
    dynamodb_table = "pawtrace-tflock"
    encrypt        = true
  }
}

provider "aws" {
  region = var.aws_region
  default_tags {
    tags = {
      Project   = var.project
      ManagedBy = "terraform"
    }
  }
}

data "aws_availability_zones" "available" {
  state = "available"
}

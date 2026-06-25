terraform {
  required_version = ">= 1.6"
  required_providers {
    aws    = { source = "hashicorp/aws", version = "~> 5.0" }
    random = { source = "hashicorp/random", version = "~> 3.0" }
  }

  # 원격 상태 (bootstrap 에서 만든 S3/DynamoDB). 처음엔 주석 처리하고 로컬 상태로 시작해도 됩니다.
  # backend "s3" {
  #   bucket         = "pawtrace-tfstate-<ACCOUNT_ID>"
  #   key            = "main/terraform.tfstate"
  #   region         = "ap-northeast-2"
  #   dynamodb_table = "pawtrace-tflock"
  #   encrypt        = true
  # }
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

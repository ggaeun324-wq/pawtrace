variable "aws_region" {
  description = "AWS 리전"
  type        = string
  default     = "ap-northeast-2"
}

variable "project" {
  description = "프로젝트 접두사"
  type        = string
  default     = "pawtrace"
}

variable "github_repo" {
  description = "OIDC 신뢰 대상 리포 (owner/repo)"
  type        = string
  default     = "ggaeun324-wq/pawtrace"
}

variable "github_branch" {
  description = "배포를 허용할 브랜치"
  type        = string
  default     = "main"
}

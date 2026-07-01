variable "aws_region" {
  type    = string
  default = "ap-northeast-2"
}

variable "project" {
  type    = string
  default = "pawtrace"
}

variable "vpc_cidr" {
  type    = string
  default = "10.0.0.0/16"
}

variable "container_image" {
  description = "ECR 이미지 URI (예: <acct>.dkr.ecr.ap-northeast-2.amazonaws.com/pawtrace-api:<tag>)"
  type        = string
  default     = "public.ecr.aws/docker/library/python:3.12-slim" # 최초 plan용 placeholder
}

variable "container_port" {
  type    = number
  default = 8000
}

variable "desired_count" {
  type    = number
  default = 1
}

variable "db_name" {
  type    = string
  default = "pawtrace"
}

variable "db_username" {
  type    = string
  default = "pawtrace"
}

variable "db_instance_class" {
  type    = string
  default = "db.t4g.micro"
}

# ── 보안 강화용 변수 (Tier 1~2) ─────────────────────────────────────
# ACM 인증서 ARN. 값이 있으면 ALB 443(HTTPS) 리스너 + HTTP→HTTPS 리다이렉트가 켜집니다.
# 도메인이 아직 없으면 빈 문자열로 두세요(HTTP 포워딩으로 동작, plan/validate 안전).
variable "acm_certificate_arn" {
  type    = string
  default = ""
}

# WAF rate-based 규칙: 5분 동안 같은 IP 허용 요청 수(무차별 로그인/스크래핑 완화).
variable "waf_rate_limit" {
  type    = number
  default = 2000
}

# Redis 전송 구간 TLS. true 면 ElastiCache transit encryption + 앱 REDIS_URL 을 rediss:// 로 사용.
variable "redis_transit_encryption" {
  type    = bool
  default = true
}

# RDS 실수 삭제 방지. 포트폴리오 teardown 편의를 위해 기본 false, 운영은 true 권장.
variable "db_deletion_protection" {
  type    = bool
  default = false
}

# ── 앱 런타임 설정/시크릿 주입용 변수 ───────────────────────────────
# 민감값(빈 값이면 앱은 stub 모드로 안전 동작). 배포 시 TF_VAR_* 또는 tfvars 로 주입.
variable "kakao_rest_api_key" {
  type      = string
  default   = ""
  sensitive = true
}

variable "public_data_api_key" {
  type      = string
  default   = ""
  sensitive = true
}

variable "admin_email" {
  type    = string
  default = "admin@pawtrace.dev"
}

variable "admin_password" {
  type      = string
  default   = "admin1234" # 데모 기본값. 운영은 반드시 tfvars/TF_VAR 로 교체.
  sensitive = true
}

# 비민감 설정
variable "bedrock_model_id" {
  type    = string
  default = "" # 예: "anthropic.claude-3-haiku-20240307-v1:0". 빈 값이면 AI stub.
}

variable "cors_origins" {
  type    = list(string)
  default = ["http://localhost:3000", "http://localhost:8777"]
}

# 앱 런타임 시크릿 — 하나의 Secrets Manager 시크릿(JSON)에 모아 ECS 로 주입합니다.
# ECS 는 valueFrom "<secretArn>:<jsonKey>::" 문법으로 개별 키만 컨테이너에 넣습니다.
# - JWT_SECRET: 코드 기본값(dev-only-change-me) 대체용으로 강한 랜덤값 자동 생성
# - 외부 API 키/관리자 비번: 변수로 주입(빈 값이면 앱이 stub/데모로 안전 동작)

resource "random_password" "jwt" {
  length  = 48
  special = false # URL/헤더 안전을 위해 특수문자 제외
}

resource "aws_secretsmanager_secret" "app" {
  name        = "${var.project}/app-secrets"
  description = "PawTrace 앱 런타임 시크릿(JWT/외부 API 키/관리자 비번)"
}

resource "aws_secretsmanager_secret_version" "app" {
  secret_id = aws_secretsmanager_secret.app.id
  secret_string = jsonencode({
    JWT_SECRET          = random_password.jwt.result
    KAKAO_REST_API_KEY  = var.kakao_rest_api_key
    PUBLIC_DATA_API_KEY = var.public_data_api_key
    ADMIN_PASSWORD      = var.admin_password
  })
}

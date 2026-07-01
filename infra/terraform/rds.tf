# RDS PostgreSQL (PostGIS는 DB에서 CREATE EXTENSION postgis 로 활성화)
resource "random_password" "db" {
  length  = 20
  special = false
}

resource "aws_db_subnet_group" "main" {
  name       = "${var.project}-db-subnets"
  subnet_ids = aws_subnet.private[*].id
}

resource "aws_db_instance" "main" {
  identifier             = "${var.project}-db"
  engine                 = "postgres"
  engine_version         = "16"
  instance_class         = var.db_instance_class
  allocated_storage      = 20
  db_name                = var.db_name
  username               = var.db_username
  password               = random_password.db.result
  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [aws_security_group.rds.id]
  skip_final_snapshot    = true # 포트폴리오/개발용. 운영에서는 false 권장
  publicly_accessible    = false
  storage_encrypted      = true

  # ── 보안/복원력 강화 ──
  deletion_protection          = var.db_deletion_protection # 실수 삭제 방지(운영 true)
  backup_retention_period      = 7                          # 자동 백업 7일 보존 → PITR 가능
  copy_tags_to_snapshot        = true
  auto_minor_version_upgrade   = true # 마이너 보안 패치 자동 적용
  performance_insights_enabled = true # 쿼리 성능 가시성(감사/튜닝)
}

# DB 접속 URL 을 Secrets Manager 에 저장 → ECS Task 가 런타임 주입
resource "aws_secretsmanager_secret" "db_url" {
  name = "${var.project}/database-url"
}

resource "aws_secretsmanager_secret_version" "db_url" {
  secret_id = aws_secretsmanager_secret.db_url.id
  secret_string = format(
    "postgresql+psycopg2://%s:%s@%s/%s",
    var.db_username,
    random_password.db.result,
    aws_db_instance.main.endpoint,
    var.db_name,
  )
}

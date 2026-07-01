# VPC Endpoints — ECS 태스크가 AWS 서비스에 붙을 때 NAT(공용 인터넷)를 타지 않고
# VPC 내부(프라이빗)로 접근하게 합니다. 보안(경계 축소) + 비용(NAT 데이터 처리료 절감) 이점.
# - S3: Gateway 엔드포인트(무료) — ECR 이미지 레이어 pull 경로도 포함
# - Secrets Manager / ECR(api,dkr) / CloudWatch Logs: Interface 엔드포인트

# 인터페이스 엔드포인트용 SG: ECS 태스크에서 오는 443 만 허용
resource "aws_security_group" "vpce" {
  name        = "${var.project}-vpce-sg"
  description = "Interface VPC endpoints - HTTPS from ECS tasks"
  vpc_id      = aws_vpc.main.id

  ingress {
    description     = "HTTPS from ECS"
    from_port       = 443
    to_port         = 443
    protocol        = "tcp"
    security_groups = [aws_security_group.ecs.id]
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# S3 Gateway 엔드포인트 — 프라이빗 라우트 테이블에 연결(무료)
resource "aws_vpc_endpoint" "s3" {
  vpc_id            = aws_vpc.main.id
  service_name      = "com.amazonaws.${var.aws_region}.s3"
  vpc_endpoint_type = "Gateway"
  route_table_ids   = [aws_route_table.private.id]
  tags              = { Name = "${var.project}-vpce-s3" }
}

# Interface 엔드포인트(프라이빗 DNS) — 필요한 서비스만 최소로
locals {
  interface_endpoints = {
    secrets = "com.amazonaws.${var.aws_region}.secretsmanager"
    ecr_api = "com.amazonaws.${var.aws_region}.ecr.api"
    ecr_dkr = "com.amazonaws.${var.aws_region}.ecr.dkr"
    logs    = "com.amazonaws.${var.aws_region}.logs"
  }
}

resource "aws_vpc_endpoint" "interface" {
  for_each            = local.interface_endpoints
  vpc_id              = aws_vpc.main.id
  service_name        = each.value
  vpc_endpoint_type   = "Interface"
  subnet_ids          = aws_subnet.private[*].id
  security_group_ids  = [aws_security_group.vpce.id]
  private_dns_enabled = true
  tags                = { Name = "${var.project}-vpce-${each.key}" }
}

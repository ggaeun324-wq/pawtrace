# ElastiCache (Redis) — P2 캐싱
resource "aws_elasticache_subnet_group" "main" {
  name       = "${var.project}-redis-subnets"
  subnet_ids = aws_subnet.private[*].id
}

resource "aws_elasticache_cluster" "redis" {
  cluster_id           = "${var.project}-redis"
  engine               = "redis"
  node_type            = "cache.t4g.micro"
  num_cache_nodes      = 1
  parameter_group_name = "default.redis7"
  port                 = 6379
  subnet_group_name    = aws_elasticache_subnet_group.main.name
  security_group_ids   = [aws_security_group.redis.id]

  # 전송 구간 TLS. 켜면 앱은 rediss:// 로 접속(app/core/cache.py 는 from_url 로 자동 호환).
  # 참고: 단일 노드 aws_elasticache_cluster 는 at-rest 암호화 인자를 지원하지 않습니다.
  #       저장 구간 암호화 + AUTH 토큰이 필요하면 aws_elasticache_replication_group 으로 전환하세요.
  transit_encryption_enabled = var.redis_transit_encryption
}

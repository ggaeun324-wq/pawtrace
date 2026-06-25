output "alb_dns_name" {
  description = "서비스 접속 주소 (http://<이 값>/api/v1/health)"
  value       = aws_lb.main.dns_name
}

output "rds_endpoint" {
  value     = aws_db_instance.main.endpoint
  sensitive = true
}

output "redis_endpoint" {
  value = aws_elasticache_cluster.redis.cache_nodes[0].address
}

output "images_bucket" {
  value = aws_s3_bucket.images.bucket
}

output "ecs_cluster" {
  value = aws_ecs_cluster.main.name
}

output "ecs_service" {
  value = aws_ecs_service.api.name
}

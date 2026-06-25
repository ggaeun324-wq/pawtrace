# PawTrace 인프라 (Terraform, P3)

AWS 인프라를 코드로 관리합니다(IaC). MVP에서는 콘솔로 빠르게 만들고,
P3에서 아래 모듈로 재현 가능하게 전환합니다.

## 구성 예정 모듈
| 모듈 | 리소스 |
|---|---|
| `network` | VPC, 퍼블릭/프라이빗 서브넷(2 AZ), NAT, 라우팅 |
| `ecs` | ECS Cluster, Fargate Service, Task Definition, ALB |
| `rds` | RDS PostgreSQL + PostGIS, 서브넷 그룹, 파라미터 그룹 |
| `cache` | ElastiCache (Redis) |
| `storage` | S3(이미지), CloudFront(OAC) |
| `ecr` | ECR 리포지토리 |
| `iam` | ECS Task Role (bedrock:InvokeModel, s3:*Object 최소권한), GitHub OIDC role |
| `observability` | CloudWatch Log Group, X-Ray |

## 보안 스캔
`terraform plan` 전후로 **Checkov / tfsec** 로 IaC 취약점을 검사합니다(CI 연동 예정).

## 사용(예정)
```bash
cd infra/terraform
terraform init
terraform plan
terraform apply
```

> 현재는 스캐폴드 단계입니다. 실제 `.tf` 파일은 P3에서 추가합니다.

# PawTrace 인프라 (Terraform IaC)

AWS 인프라를 코드로 관리합니다. `terraform validate` 통과 상태입니다.

## 구성
```
infra/terraform/
├─ bootstrap/        1회 실행: GitHub OIDC + 배포 Role + ECR + tfstate(S3/DynamoDB)
├─ providers.tf      provider/버전, 원격 상태(주석)
├─ variables.tf      리전·이미지·DB 등 입력값
├─ network.tf        VPC, 퍼블릭/프라이빗 서브넷(2 AZ), IGW, NAT
├─ security.tf       Security Group (ALB→ECS→RDS/Redis 최소권한)
├─ alb.tf            ALB + Target Group + Listener(/api/v1/health)
├─ ecs.tf            ECS Cluster, IAM(Execution/Task), Task Def, Service, 로그
├─ rds.tf            RDS PostgreSQL + Secrets Manager(DB URL)
├─ cache.tf          ElastiCache(Redis)
├─ s3.tf             이미지 버킷(비공개)
└─ outputs.tf        ALB DNS 등 출력
```

## 배포 순서

### 1) Bootstrap (1회, 로컬)
```bash
cd infra/terraform/bootstrap
terraform init && terraform apply
# 출력된 deploy_role_arn / ecr_repository_url 기록
```
→ GitHub 등록:
```bash
gh secret set AWS_DEPLOY_ROLE_ARN -R ggaeun324-wq/pawtrace --body "<deploy_role_arn>"
gh variable set DEPLOY_ENABLED   -R ggaeun324-wq/pawtrace --body "true"
```

### 2) 메인 인프라
```bash
cd infra/terraform
terraform init
terraform apply -var="container_image=<ECR_URL>:<tag>"
# 출력된 alb_dns_name 으로 접속: http://<alb_dns_name>/api/v1/health
```

### 3) 이후 배포
`main` 브랜치 푸시 → `deploy.yml` 이 이미지 빌드 → Trivy 스캔 → ECR push → ECS 롤링 업데이트.

## 비용 주의 ⚠️
NAT Gateway·RDS·ElastiCache·ALB 는 시간당 과금됩니다. 학습/포트폴리오 용도라면
사용 후 `terraform destroy` 로 정리하세요. (단일 NAT·t4g.micro 로 비용 최소화)

## 보안 스캔 (예정)
CI에 **Checkov / tfsec** 를 붙여 `terraform plan` 전에 IaC 취약점을 검사합니다.

## PostGIS 활성화
RDS 생성 후 1회: `CREATE EXTENSION IF NOT EXISTS postgis;`

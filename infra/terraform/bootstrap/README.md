# Bootstrap (1회 실행)

GitHub Actions가 **키 없이(OIDC)** AWS에 배포하도록 기반을 만듭니다.

## 생성되는 것
- GitHub OIDC Provider
- 배포용 IAM Role (`pawtrace-gha-deploy`) — 이 리포 `main`에서만 assume 가능
- ECR 리포지토리 (`pawtrace-api`)
- Terraform 원격 상태용 S3 버킷 + DynamoDB 잠금 테이블

## 실행 (로컬, 관리자 자격증명 필요)
```bash
# AWS 자격증명 설정 (둘 중 하나)
aws configure                 # 또는
export AWS_ACCESS_KEY_ID=...   AWS_SECRET_ACCESS_KEY=...

cd infra/terraform/bootstrap
terraform init
terraform apply
```

## apply 후 → GitHub에 등록
출력된 값을 등록합니다.
```bash
# Secret
gh secret set AWS_DEPLOY_ROLE_ARN -R ggaeun324-wq/pawtrace --body "<deploy_role_arn 출력값>"
# Variable (deploy 워크플로 활성화)
gh variable set DEPLOY_ENABLED -R ggaeun324-wq/pawtrace --body "true"
```

> ⚠️ 이 단계는 자격증명이 필요해 **회원님 로컬에서** 실행해야 합니다. (CI에서 만들지 않음)

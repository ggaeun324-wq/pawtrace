# AWS WAF v2 — 인터넷 노출 ALB 앞단 L7 방어
# - AWS 관리형 규칙: 공통 취약점(OWASP 유사) + 알려진 악성 입력 패턴
# - Rate-based 규칙: 같은 IP 의 폭주(무차별 로그인/스크래핑) 완화
# 비용: Web ACL($5/월) + 규칙($1/월·개) + 요청 100만건당 $0.60 수준.

resource "aws_wafv2_web_acl" "alb" {
  name        = "${var.project}-web-acl"
  description = "PawTrace ALB protection (managed rules + rate limit)"
  scope       = "REGIONAL" # ALB = REGIONAL (CloudFront 는 CLOUDFRONT)

  default_action {
    allow {}
  }

  # 1) AWS 공통 관리형 규칙(SQLi/XSS/LFI 등 광범위 보호)
  rule {
    name     = "AWSCommonRules"
    priority = 1
    override_action {
      none {}
    }
    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesCommonRuleSet"
        vendor_name = "AWS"
      }
    }
    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "${var.project}-common"
      sampled_requests_enabled   = true
    }
  }

  # 2) 알려진 악성 입력(취약 경로/헤더 페이로드 등)
  rule {
    name     = "AWSKnownBadInputs"
    priority = 2
    override_action {
      none {}
    }
    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesKnownBadInputsRuleSet"
        vendor_name = "AWS"
      }
    }
    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "${var.project}-badinputs"
      sampled_requests_enabled   = true
    }
  }

  # 3) IP 기반 rate limit — 5분 창에서 임계치 초과 IP 차단
  rule {
    name     = "RateLimit"
    priority = 3
    action {
      block {}
    }
    statement {
      rate_based_statement {
        limit              = var.waf_rate_limit
        aggregate_key_type = "IP"
      }
    }
    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "${var.project}-ratelimit"
      sampled_requests_enabled   = true
    }
  }

  visibility_config {
    cloudwatch_metrics_enabled = true
    metric_name                = "${var.project}-web-acl"
    sampled_requests_enabled   = true
  }
}

resource "aws_wafv2_web_acl_association" "alb" {
  resource_arn = aws_lb.main.arn
  web_acl_arn  = aws_wafv2_web_acl.alb.arn
}

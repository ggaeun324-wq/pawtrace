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

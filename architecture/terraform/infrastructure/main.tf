provider "aws" {
    region = var.AWS_REGION
    access_key = var.AWS_ACCESS_KEY
    secret_key = var.AWS_SECRET_KEY
}

# RDS
resource "aws_security_group" "db-security-group" {
    name = "museum-db-sg"
    vpc_id = var.CURRENT_VPC_ID
}

resource "aws_vpc_security_group_ingress_rule" "db-sg-inbound-rule" {
    security_group_id = aws_security_group.db-security-group.id
    cidr_ipv4 = "0.0.0.0/0"
    from_port = 5432
    to_port = 5432
    ip_protocol = "tcp"
}

resource "aws_db_instance" "museum-db" {
    allocated_storage = 10
    db_name = var.DATABASE_NAME
    engine = "postgres"
    identifier = "museum-db"
    engine_version = "17.2"
    instance_class = "db.t3.micro"
    publicly_accessible = true
    performance_insights_enabled = false
    skip_final_snapshot = true
    db_subnet_group_name = var.PUBLIC_SUBNET_GROUP_NAME
    vpc_security_group_ids = [aws_security_group.db-security-group.id]
    username = var.DATABASE_USERNAME
    password = var.DATABASE_PASSWORD
}

# ECR
data "aws_ecr_image" "scheduler_image" {
    repository_name = "c17-football-scheduler-ecr"
    image_tag = "latest"
}

data "aws_ecr_image" "match_seeder_image" {
    repository_name = "c17-football-match-seeder-ecr"
    image_tag = "latest"
}

data "aws_ecr_image" "pipeline_image" {
    repository_name = "c17-football-pipeline-ecr"
    image_tag = "latest"
}

data "aws_ecr_image" "notification_image" {
    repository_name = "c17-football-notification-ecr"
    image_tag = "latest"
}

data "aws_ecr_image" "report_image" {
    repository_name = "c17-football-report-ecr"
    image_tag = "latest"
}

data "aws_ecr_image" "scheduler_stopper_image" {
    repository_name = "c17-football-scheduler-stopper-ecr"
    image_tag = "latest"
}

data "aws_vpc" "current-vpc" {
    id = "vpc-00b3f6b2893c390f2"
}

data "aws_iam_policy" "cloudwatch_full_access" {
    arn = "arn:aws:iam::aws:policy/CloudWatchLogsFullAccess"
}

data "aws_iam_policy" "ecr_full_access" {
    arn = "arn:aws:iam::aws:policy/AmazonElasticContainerRegistryPublicFullAccess"
}


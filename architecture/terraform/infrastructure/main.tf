provider "aws" {
    region = var.AWS_REGION
    access_key = var.AWS_ACCESS_KEY
    secret_key = var.AWS_SECRET_KEY
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




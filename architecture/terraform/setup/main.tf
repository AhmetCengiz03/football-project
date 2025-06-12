provider "aws" {
    region = var.AWS_REGION
    access_key = var.AWS_ACCESS_KEY
    secret_key = var.AWS_SECRET_KEY
}

resource "aws_ecr_repository" "scheduler_repo" {
    name = "c17-football-scheduler-ecr"
    image_tag_mutability = "MUTABLE"
    image_scanning_configuration {
      scan_on_push = true
    }
    force_delete = true
}

resource "aws_ecr_repository" "match_seeder_repo" {
    name = "c17-football-match-seeder-ecr"
    image_tag_mutability = "MUTABLE"
    image_scanning_configuration {
      scan_on_push = true
    }
    force_delete = true
}

resource "aws_ecr_repository" "pipeline_repo" {
    name = "c17-football-pipeline-ecr"
    image_tag_mutability = "MUTABLE"
    image_scanning_configuration {
      scan_on_push = true
    }
    force_delete = true
}

resource "aws_ecr_repository" "notification_repo" {
    name = "c17-football-notification-ecr"
    image_tag_mutability = "MUTABLE"
    image_scanning_configuration {
      scan_on_push = true
    }
    force_delete = true
}

resource "aws_ecr_repository" "report_repo" {
    name = "c17-football-report-ecr"
    image_tag_mutability = "MUTABLE"
    image_scanning_configuration {
      scan_on_push = true
    }
    force_delete = true
}

resource "aws_ecr_repository" "scheduler_stopper_repo" {
    name = "c17-football-scheduler-stopper-ecr"
    image_tag_mutability = "MUTABLE"
    image_scanning_configuration {
      scan_on_push = true
    }
    force_delete = true
}


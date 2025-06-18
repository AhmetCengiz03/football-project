provider "aws" {
    region = var.AWS_REGION
    access_key = var.AWS_ACCESS_KEY
    secret_key = var.AWS_SECRET_KEY
}

data "aws_vpc" "current-vpc" {
    id = var.CURRENT_VPC_ID
}

# RDS
resource "aws_security_group" "db-security-group" {
    name = "c17-football-db-sg"
    vpc_id = var.CURRENT_VPC_ID
}

resource "aws_vpc_security_group_ingress_rule" "db-sg-inbound-rule" {
    security_group_id = aws_security_group.db-security-group.id
    cidr_ipv4 = "0.0.0.0/0"
    from_port = 5432
    to_port = 5432
    ip_protocol = "tcp"
}

resource "aws_db_instance" "football-db" {
    allocated_storage = 10
    db_name = var.DATABASE_NAME
    engine = "postgres"
    identifier = "c17-football-db"
    engine_version = "17.4"
    instance_class = "db.t3.micro"
    publicly_accessible = true
    performance_insights_enabled = false
    skip_final_snapshot = true
    db_subnet_group_name = var.PUBLIC_SUBNET_GROUP_NAME
    vpc_security_group_ids = [aws_security_group.db-security-group.id]
    username = var.DATABASE_USERNAME
    password = var.DATABASE_PASSWORD
}

# S3 BUCKET
resource "aws_s3_bucket" "s3_bucket" {
    bucket = "c17-football-report-bucket"
    force_destroy = true
}

resource "aws_s3_object" "report_folder" {
  bucket = aws_s3_bucket.s3_bucket.id
  key    = "reports/"
  content = ""
}


# SNS Topic
resource "aws_sns_topic" "report-topic" {
  name  = "c17-football-topic"

  tags = {
    Environment = "dev"
    Terraform   = "true"
  }
}

resource "aws_sns_topic_subscription" "email_subscription" {
  topic_arn = aws_sns_topic.report-topic.arn
  protocol    = "email"
  endpoint    = "trainee.raf.hall@sigmalabs.co.uk"
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


# LAMBDAS
resource "aws_iam_role" "lambda_role" {
    name = "c17-football-lambda-role"
    assume_role_policy = jsonencode({
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "lambda.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            },
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "scheduler.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    })
}

resource "aws_iam_policy" "lambda_policy" {
  name        = "c17-football-lambda-policy"
  description = "Allows Lambdas to run access S3, write logs, query a postgres RDS and allow SNS and SES messages."

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [

        {
        Sid    = "S3Access",
        Effect = "Allow",
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:ListBucket",
          "s3:DeleteObject",
          "s3:GetBucketLocation"
        ],
        Resource = [
          "arn:aws:s3:::${aws_s3_bucket.s3_bucket.bucket}",
          "arn:aws:s3:::${aws_s3_bucket.s3_bucket.bucket}/*"
        ]
        },
        {
        Sid    = "CloudWatchLogs",
        Effect = "Allow",
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ],
        Resource = "*"
        },
        {
        "Sid": "PublishSNSMessage",
        "Effect": "Allow",
        "Action": "sns:Publish",
        "Resource": aws_sns_topic.report-topic.arn
        },
        {
        "Sid": "SESv2EmailAccess",
        "Effect": "Allow",
        "Action": [
          "sesv2:SendEmail"
        ],
        "Resource": "*"
        },
        {
        "Sid": "RDSAccess",
        "Effect": "Allow",
        "Action": [
          "rds:DescribeDBInstances",
          "rds:DescribeDBClusters"
        ],
        "Resource": "*"
        },
        {
        Sid    = "EventBridgeSchedulerAccess",
        Effect = "Allow",
        Action = [
          "scheduler:CreateSchedule",
          "scheduler:CreateScheduleGroup",
          "scheduler:GetSchedule",
          "scheduler:ListSchedules",
          "scheduler:ListScheduleGroups",
          "scheduler:UpdateSchedule",
          "scheduler:DeleteSchedule",
          "scheduler:DeleteScheduleGroup"
        ],
        Resource = "*"
      },
      {
        Sid = "PassRole",
        Effect = "Allow",
        Action =[
          "iam:PassRole"
        ]
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_role_attach" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.lambda_policy.arn
}

resource "aws_lambda_function" "match_seeder_lambda" {
    depends_on = [ aws_iam_role_policy_attachment.lambda_role_attach ]
    timeout = 900
    memory_size = 512

    function_name = "c17-football-match-seeder-lambda"
    role          = aws_iam_role.lambda_role.arn

    package_type = "Image"
    image_uri = data.aws_ecr_image.match_seeder_image.image_uri

    environment {
        variables = {
            DB_HOST=var.DATABASE_HOST
            DB_PORT=var.DATABASE_PORT
            DB_USER=var.DATABASE_USERNAME
            DB_PASSWORD=var.DATABASE_PASSWORD
            DB_NAME=var.DATABASE_NAME
            SPORTMONKS_API_TOKEN=var.API_KEY
        }
    }
}

resource "aws_lambda_function" "scheduler_lambda" {
    depends_on = [ aws_iam_role_policy_attachment.lambda_role_attach ]
    timeout = 120
    memory_size = 512

    function_name = "c17-football-scheduler-lambda"
    role          = aws_iam_role.lambda_role.arn

    package_type = "Image"
    image_uri = data.aws_ecr_image.scheduler_image.image_uri

    environment {
        variables = {
          API_KEY=var.API_KEY
          TARGET_ARN=var.PIPELINE_ARN
          ROLE_ARN=var.PIPELINE_ROLE_ARN
          AWS_REGION_NAME=var.AWS_REGION
        }         
    }
}


resource "aws_lambda_function" "pipeline_lambda" {
    depends_on = [ aws_iam_role_policy_attachment.lambda_role_attach ]
    timeout = 120
    memory_size = 512

    function_name = "c17-football-pipeline-lambda"
    role          = aws_iam_role.lambda_role.arn

    package_type = "Image"
    image_uri = data.aws_ecr_image.pipeline_image.image_uri

    environment {
        variables = {
            DB_HOST=var.DATABASE_HOST
            DB_PORT=var.DATABASE_PORT
            DB_USER=var.DATABASE_USERNAME
            DB_PASS=var.DATABASE_PASSWORD
            DB_NAME=var.DATABASE_NAME
            TOKEN=var.API_KEY
            BASE_URL=var.BASE_URL
        }
    }
}

resource "aws_lambda_function" "notification_lambda" {
    depends_on = [ aws_iam_role_policy_attachment.lambda_role_attach ]
    timeout = 120
    memory_size = 512

    function_name = "c17-football-notification-lambda"
    role          = aws_iam_role.lambda_role.arn

    package_type = "Image"
    image_uri = data.aws_ecr_image.notification_image.image_uri

    environment {
        variables = {
            TOPIC_ARN=aws_sns_topic.report-topic.arn

        }
    }
}


resource "aws_lambda_function" "report_lambda" {
    depends_on = [ aws_iam_role_policy_attachment.lambda_role_attach ]
    timeout = 120
    memory_size = 512

    function_name = "c17-football-report-lambda"
    role          = aws_iam_role.lambda_role.arn

    package_type = "Image"
    image_uri = data.aws_ecr_image.report_image.image_uri

    environment {
        variables = {
          DB_NAME=var.DATABASE_NAME
          DB_HOST=var.DATABASE_HOST
          DB_USER=var.DATABASE_USERNAME
          DB_PASSWORD=var.DATABASE_PASSWORD
          DB_PORT=var.DATABASE_PORT

          OPENAI_API_KEY=var.OPEN_AI_API_KEY
          S3_BUCKET=var.S3_BUCKET
        }
    }
}

resource "aws_lambda_function" "scheduler_stopper_lambda" {
    depends_on = [ aws_iam_role_policy_attachment.lambda_role_attach ]
    timeout = 120
    memory_size = 512

    function_name = "c17-football-scheduler-stopper-lambda"
    role          = aws_iam_role.lambda_role.arn

    package_type = "Image"
    image_uri = data.aws_ecr_image.scheduler_stopper_image.image_uri
    environment {
        variables = {
            AWS_REGION_NAME=var.AWS_REGION
        }
    }
}


# Eventbridge Scheduler
resource "aws_iam_role" "scheduler_role" {
  name = "c17-football-daily"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
        {
            Action = "sts:AssumeRole"
            Effect = "Allow"
            Principal = {
                Service = "scheduler.amazonaws.com"
            }
        }
    ]
  })
}

resource "aws_iam_role_policy" "eventbridge_invoke_policy" {
  name = "EventBridgeInvokePolicy"
  role = aws_iam_role.scheduler_role.id
  policy = jsonencode({
    "Version"   : "2012-10-17",
    "Statement" : [
        {
            "Sid"       : "AllowEventBridgeToInvokeLambda",
            "Action"    : ["states:StartExecution"],
            "Effect"    : "Allow",
            "Resource"  : [
              var.SCHEDULE_ARN
            ]
        }
    ] 
  })
}

resource "aws_scheduler_schedule" "daily_schedule" {
  name       = "c17-football-daily-schedule"
  group_name = "default"

  flexible_time_window {
    mode = "OFF"
  }

  schedule_expression =  "cron(50 22 * * ? *)"

  target {
    arn      = var.SCHEDULE_ARN
    role_arn = aws_iam_role.scheduler_role.arn
  }
}
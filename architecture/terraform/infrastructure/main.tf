provider "aws" {
    region = var.AWS_REGION
    access_key = var.AWS_ACCESS_KEY
    secret_key = var.AWS_SECRET_KEY
}

data "aws_vpc" "current-vpc" {
    id = var.CURRENT_VPC_ID
}

data "aws_iam_policy" "cloudwatch_full_access" {
    arn = "arn:aws:iam::aws:policy/CloudWatchLogsFullAccess"
}

data "aws_iam_policy" "ecr_full_access" {
    arn = "arn:aws:iam::aws:policy/AmazonElasticContainerRegistryPublicFullAccess"
}

data "aws_iam_policy" "RDS_full_access" {
    arn = "arn:aws:iam::aws:policy/AmazonRDSFullAccess"
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



# LAMBDA

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
        "Sid": "PublishSESMessage",
        "Effect": "Allow",
        "Action": "sns:Publish",
        "Resource": aws_sns_topic.report-topic.arn
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_role_attach" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.lambda_policy.arn
}

resource "aws_lambda_function" "report_lambda" {
    depends_on = [ aws_iam_role_policy_attachment.lambda_role_attach ]
    timeout = 120
    memory_size = 512

    function_name = "c17-cattus-report-lambda"
    role          = aws_iam_role.lambda_role.arn

    package_type = "Image"
    image_uri = data.aws_ecr_image.report_image.image_uri

    environment {
        variables = {
            DB_HOST=var.DATABASE_HOST
            DB_PORT=var.DATABASE_PORT
            DB_USER=var.DATABASE_USERNAME
            DB_PASSWORD=var.DATABASE_PASSWORD
            DB_NAME=var.DATABASE_NAME
            TOPIC_REGION=var.AWS_REGION
            TOPIC_ARN=aws_sns_topic.report-topic.arn
        }
    }
}

resource "aws_lambda_function" "short_pipeline_lambda" {
    depends_on = [ aws_iam_role_policy_attachment.lambda_role_attach ]
    timeout = 120
    memory_size = 512

    function_name = "c17-cattus-short-pipeline-lambda"
    role          = aws_iam_role.lambda_role.arn

    package_type = "Image"
    image_uri = data.aws_ecr_image.short_pipe_image.image_uri

    environment {
        variables = {
            DB_HOST=var.DB_HOST
            DB_PORT=var.DB_PORT
            DB_USER=var.DB_USER
            DB_PASSWORD=var.DB_PASSWORD
            DB_NAME=var.DB_NAME
            DB_SCHEMA=var.DB_SCHEMA
            S3_BUCKET=aws_s3_bucket.s3_bucket.bucket
        }
    }
}

resource "aws_lambda_function" "long_pipeline_lambda" {
    depends_on = [ aws_iam_role_policy_attachment.lambda_role_attach ]
    timeout = 120
    memory_size = 512

    function_name = "c17-cattus-long-pipeline-lambda"
    role          = aws_iam_role.lambda_role.arn

    package_type = "Image"
    image_uri = data.aws_ecr_image.long_pipe_image.image_uri

    environment {
        variables = {
            DB_HOST=var.DB_HOST
            DB_PORT=var.DB_PORT
            DB_USER=var.DB_USER
            DB_PASSWORD=var.DB_PASSWORD
            DB_NAME=var.DB_NAME
            DB_SCHEMA=var.DB_SCHEMA
            S3_BUCKET=aws_s3_bucket.s3_bucket.bucket
        }
    }
}
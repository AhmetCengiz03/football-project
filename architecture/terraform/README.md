# Terraform

## Setup
- This directory provides infrastructure as code for the full pipeline cloud system
- The two sub directories constitute a setup of resources that require manual input and the rest of the infrastructure
    1) Navigate to the `/setup` subdirectory and follow the steps in the README.
    2) Navigate to `/infrastructure` and follow the steps in the README.

## `setup`
- Creates 6 elastic container registries
- They are responsible for storing each of the separate Lambda functions.

## `push_ecr_*` scripts
- This should be ran after the setup stage.
- Each file should be ran once.
- It will load a docker image into an ecr.

## `infrastructure`
- Creates the full cloud architecture
- Includes lambda functions, an S3 bucket, the RDS database for the project, the Event bridge scheduler and SNS topic.


**DISCLAIMER**

Step Functions used in this project must be made using the AWS Console. Follow Architecture Diagram to know what goes in these step functions.
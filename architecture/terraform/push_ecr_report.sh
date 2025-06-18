cd ../../report
aws ecr get-login-password --region eu-west-2 | docker login --username AWS --password-stdin 129033205317.dkr.ecr.eu-west-2.amazonaws.com
docker build --provenance=false --platform=linux/amd64  -t c17-football-report-ecr .
docker tag c17-football-report-ecr:latest 129033205317.dkr.ecr.eu-west-2.amazonaws.com/c17-football-report-ecr:latest
docker push 129033205317.dkr.ecr.eu-west-2.amazonaws.com/c17-football-report-ecr:latest

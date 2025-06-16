read -p 'image_name: ' image_name
read -p 'ecr_address: ' ecr
read -p 'folder with Dockerfile: ' folder

cd ../../$folder
aws ecr get-login-password --region eu-west-2 | docker login --username AWS --password-stdin $ecr
docker build --provenance=false --platform=linux/amd64  -t $image_name .
docker tag $image_name:latest $ecr/$image_name:latest
docker push $ecr/$image_name:latest
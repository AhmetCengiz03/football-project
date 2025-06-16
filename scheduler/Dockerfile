FROM public.ecr.aws/lambda/python:latest

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY scheduler.py .

CMD ["scheduler.lambda_handler"]
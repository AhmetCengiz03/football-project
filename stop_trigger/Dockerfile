FROM public.ecr.aws/lambda/python:latest

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY stop_trigger.py .

CMD ["stop_trigger.lambda_handler"]
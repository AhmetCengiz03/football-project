FROM public.ecr.aws/lambda/python:latest

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY extract.py .
COPY transform.py .
COPY load.py .
COPY pipeline.py .

CMD ["pipeline.lambda_handler"]
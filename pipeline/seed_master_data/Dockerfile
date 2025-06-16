FROM public.ecr.aws/lambda/python:latest

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY extract_transform.py .
COPY load_data.py .
COPY handler.py .

CMD ["handler.lambda_handler"]
FROM public.ecr.aws/lambda/python:latest

WORKDIR ${LAMBDA_TASK_ROOT}

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY types_map_api.xlsx .
COPY extract.py .
COPY transform.py .
COPY load.py .
COPY pipeline.py .

CMD ["pipeline.lambda_handler"]
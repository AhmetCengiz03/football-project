FROM public.ecr.aws/lambda/python:latest

WORKDIR ${LAMBDA_TASK_ROOT}

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY report_data.py .
COPY report_commentary.py .
COPY html_report.py .
COPY report.py .

CMD [ "report.lambda_handler" ]
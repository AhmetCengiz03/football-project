import logging
from os import makedirs, environ as ENV
from os.path import join

from dotenv import load_dotenv
from xhtml2pdf import pisa
from boto3 import client
from botocore.exceptions import ClientError

from report_commentary import generate_match_report
from html_report import generate_html


def connect_to_s3_client(config) -> client:
    """Connects to the S3 bucket."""
    return client("s3",  aws_access_key_id=config["AWS_ACCESS_KEY_ID"],
                  aws_secret_access_key=config["AWS_SECRET_ACCESS_KEY"],
                  aws_session_token=config["AWS_SESSION_TOKEN"])


def upload_file(config: dict, local_path: str, s3_name: str) -> bool:
    """Upload a file to an S3 bucket."""

    s3_client = connect_to_s3_client(config)

    try:
        s3_client.upload_file(local_path, config["S3_BUCKET"], s3_name)
        return True

    except ClientError as e:
        logging.error(e)
        return False


def html_to_pdf(html_content: str, output_path: str) -> bool:
    """Convert HTML to PDF using xhtml2pdf."""
    try:
        with open(output_path, "wb") as result_file:
            pdf = pisa.CreatePDF(html_content, dest=result_file)
        return not pdf.err
    except Exception as e:
        logging.error("Error creating PDF: %s", e)
        return False


def generate_complete_report(config: dict, match_id: int, output_dir: str,
                             sender_email: str = None, recipient_email: str = None) -> dict[str, str]:
    """Generate complete match report with HTML, PDF, and email."""

    makedirs(output_dir, exist_ok=True)

    logging.info("Generating AI analysis for match %s...", match_id)
    report = generate_match_report(config, match_id)

    logging.info("Creating HTML report...")
    html_content = generate_html(report)

    logging.info("Converting to PDF...")
    pdf_filename = f"match_{match_id}_report.pdf"
    pdf_path = join(output_dir, pdf_filename)
    pdf_success = html_to_pdf(html_content, pdf_path)
    if pdf_success:
        upload_file(config, pdf_path, f"reports/{pdf_filename}")


def lambda_handler(event, context) -> None:
    """
    AWS Lambda handler function.

    Args:
        event: Lambda event data
        context: Lambda context object
    """
    load_dotenv()

    match_id = event["match_id"]
    if not match_id:
        raise ValueError("match_id is required in the event")

    generate_complete_report(
        ENV,
        match_id,
        output_dir="/tmp/reports",
    )


if __name__ == "__main__":
    load_dotenv()

    match_id = 19367880

    generate_complete_report(
        ENV,
        match_id,
        output_dir="reports",
    )

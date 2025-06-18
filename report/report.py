import logging
from os import makedirs, environ as ENV
from os.path import basename, join
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

from dotenv import load_dotenv
from xhtml2pdf import pisa
from boto3 import client
from botocore.exceptions import ClientError

from report_commentary import generate_match_report
from html_report import generate_html


def connect_to_s3_client(config) -> client:
    """Connects to the S3 bucket."""
    return client("s3",  aws_access_key_id=config["AWS_ACCESS_KEY_ID"],
                  aws_secret_access_key=config["AWS_SECRET_ACCESS_KEY"])


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
        print(f"Error creating PDF: {e}")
        return False


def create_email_message(pdf_path: str, match_title: str,
                         sender_email: str, recipient_email: str) -> MIMEMultipart:
    """Create email message with PDF attachment."""

    msg = MIMEMultipart('mixed')
    msg['Subject'] = f"Match Report: {match_title}"
    msg['From'] = sender_email
    msg['To'] = recipient_email

    msg_body = MIMEMultipart('alternative')
    body_text = f"""
    Dear Football Fan,
    
    Please find attached the detailed match report for: {match_title}
    
    This comprehensive report includes:
    - Complete match analysis
    - Period-by-period breakdown
    - Key events and player performances
    - Expert commentary and insights
    
    Best regards,
    PlayByPlay Insights Team
    """

    textpart = MIMEText(body_text, 'plain')
    msg_body.attach(textpart)
    msg.attach(msg_body)

    with open(pdf_path, 'rb') as f:
        part = MIMEApplication(f.read())
        part.add_header('Content-Disposition', 'attachment',
                        filename=basename(pdf_path))
        msg.attach(part)

    return msg


def generate_complete_report(config: dict, match_id: int, output_dir: str = "reports",
                             sender_email: str = None, recipient_email: str = None) -> dict[str, str]:
    """Generate complete match report with HTML, PDF, and email."""

    makedirs(output_dir, exist_ok=True)

    print(f"Generating AI analysis for match {match_id}...")
    report = generate_match_report(config, match_id)

    print("Creating HTML report...")
    html_content = generate_html(report)

    print("Converting to PDF...")
    pdf_filename = f"match_{match_id}_report.pdf"
    pdf_path = join(output_dir, pdf_filename)
    pdf_success = html_to_pdf(html_content, pdf_path)
    if pdf_success:
        upload_file(config, pdf_path, f"reports/{pdf_filename}")

    results = {
        'html_path': html_path,
        'pdf_path': pdf_path if pdf_success else None,
        'report_data': report.model_dump()
    }

    if sender_email and recipient_email and pdf_success:
        print("Creating email message...")
        email_msg = create_email_message(
            pdf_path, report.match_title, sender_email, recipient_email
        )
        results['email_message'] = email_msg.as_string()

    print(f"Report generation complete! Files saved to {output_dir}")
    return results


def lambda_handler(event, context) -> None:
    """
    AWS Lambda handler function.

    Args:
        event: Lambda event data
        context: Lambda context object

    Returns:
        Dictionary with status code and response body
    """
    load_dotenv()

    match_id = event["match_id"]
    if not match_id:
        raise ValueError("match_id is required in the event")

    generate_complete_report(
        ENV,
        match_id,
        output_dir="reports",
        sender_email="trainee.ahmet.cengiz@sigmalabs.co.uk",
        recipient_email="trainee.ahmet.cengiz@sigmalabs.co.uk"
    )


if __name__ == "__main__":
    load_dotenv()

    match_id = 19367880

    generate_complete_report(
        ENV,
        match_id,
        output_dir="reports",
        sender_email="trainee.ahmet.cengiz@sigmalabs.co.uk",
        recipient_email="trainee.ahmet.cengiz@sigmalabs.co.uk"
    )

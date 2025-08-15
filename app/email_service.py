import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from .models import Submission
import os
from typing import Dict


class EmailService:
    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER")
        self.smtp_password = os.getenv("SMTP_PASSWORD")

        # Map domains to recipient HR emails
        self.recipient_map: Dict[str, str] = {
            "gktechnologies.com": os.getenv("GK_EMAIL"),
            "dglobaltech.com": os.getenv("DBTECH_EMAIL"),
            "localhost": os.getenv("SMTP_USER"),  # For local testing
        }

    def _create_email_content(self, submission: Submission, recipient_email: str) -> MIMEMultipart:
        msg = MIMEMultipart()
        msg["From"] = self.smtp_user
        msg["To"] = recipient_email
        msg["Subject"] = f"New Career Submission - {submission.full_name}"

        html_content = f"""
        <html>
        <body>
        <h2>New Candidate Submission</h2>
        <table border="1" cellpadding="6" cellspacing="0" style="border-collapse: collapse;">
            <tr><th>Full Name</th><td>{submission.full_name}</td></tr>
            <tr><th>Email</th><td>{submission.email}</td></tr>
            <tr><th>Phone</th><td>{submission.phone}</td></tr>
            <tr><th>LinkedIn</th><td><a href="{submission.linkedin}">{submission.linkedin}</a></td></tr>
            <tr><th>Role</th><td>{submission.role}</td></tr>
            <tr><th>Work Authorization</th><td>{submission.work_auth_status}</td></tr>
            <tr><th>Preferred Location</th><td>{submission.preferred_location}</td></tr>
            <tr><th>Availability</th><td>{submission.availability}</td></tr>
            <tr><th>Comments</th><td>{submission.comments}</td></tr>
            <tr><th>Resume Link</th><td><a href="{submission.resume_url}">Download Resume</a></td></tr>
        </table>
        </body>
        </html>
        """
        msg.attach(MIMEText(html_content, "html"))
        return msg

    def _attach_resume_from_bytes(self, msg: MIMEMultipart, filename: str, file_bytes: bytes):
        part = MIMEBase("application", "octet-stream")
        part.set_payload(file_bytes)
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f"attachment; filename={filename}")
        msg.attach(part)

    async def send_email(self, submission: Submission, filename: str, file_bytes: bytes):
        try:
            recipient_email = self.recipient_map.get(submission.origin_domain)
            if not recipient_email:
                raise ValueError(f"No recipient email configured for domain: {submission.origin_domain}")

            msg = self._create_email_content(submission, recipient_email)
            self._attach_resume_from_bytes(msg, filename, file_bytes)

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)

            print(f"✅ Email sent to {recipient_email}")
        except Exception as e:
            print(f"Error sending email: {str(e)}")

email_service = EmailService()
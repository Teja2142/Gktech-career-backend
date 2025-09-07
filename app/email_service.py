import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from .models import Submission
import os
from typing import Dict, Optional
from .company_config import CompanyConfig


class EmailService:
    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER")
        self.smtp_password = os.getenv("SMTP_PASSWORD")

        # Map domains to recipient HR emails (can be overridden by env)
        self.recipient_map: Dict[str, str] = {
            "kgktechnologies.com": os.getenv("GK_EMAIL"),
            "gktechnologies.com": os.getenv("GK_EMAIL"),
            "dglobaltech.com": os.getenv("DBTECH_EMAIL"),
            "dglobal.com": os.getenv("DBTECH_EMAIL"),
            "localhost": os.getenv("SMTP_USER"),  # For local testing
        }

    def get_recipient(self, domain: Optional[str]) -> Optional[str]:
        """Resolve HR recipient for a domain using multiple strategies.

        1. Exact match in recipient_map
        2. CompanyConfig mapping
        3. Suffix match (example: domain endswith known key)
        """
        if not domain:
            return None

        # exact lookup
        recipient = self.recipient_map.get(domain)
        if recipient:
            return recipient

        # company config mapping
        recipient = CompanyConfig.get_hr_email(domain)
        if recipient:
            return recipient

        # try suffix matches (e.g., submitted domain may include subdomain)
        for k, v in self.recipient_map.items():
            if domain.endswith(k):
                return v

        return None

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

    def send_email(self, submission: Submission, filename: str, file_bytes: bytes) -> bool:
        try:
            recipient_email = self.get_recipient(submission.origin_domain)
            if not recipient_email:
                raise ValueError(f"No recipient email configured for domain: {submission.origin_domain}")

            msg = self._create_email_content(submission, recipient_email)
            self._attach_resume_from_bytes(msg, filename, file_bytes)

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                if self.smtp_user and self.smtp_password:
                    server.login(self.smtp_user, self.smtp_password)
                server.sendmail(msg["From"], [recipient_email], msg.as_string())

            print(f"✅ Email sent to {recipient_email}")
            return True
        except Exception as e:
            print(f"Error sending email: {str(e)}")
            return False

    def _send_smtp_message(self, msg: MIMEMultipart, recipients) -> bool:
        """Open SMTP connection, start TLS, optionally login, send message."""
        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.ehlo()
                server.starttls()
                server.ehlo()
                if self.smtp_user and self.smtp_password:
                    # login per connection; required for authenticated SMTP servers
                    server.login(self.smtp_user, self.smtp_password)
                server.sendmail(msg["From"], recipients, msg.as_string())
            return True
        except Exception as exc:
            print(f"SMTP send failed: {exc}")
            return False

    def send_contact_email(self, contact, domain: Optional[str] = None) -> bool:
        """Send contact form email.

        If `domain` is provided, resolve the HR recipient for that domain. Otherwise
        fall back to CONTACT_RECEIVER or SMTP_USER.
        """
        # Determine recipient: try domain-based routing first
        recipient = None
        if domain:
            recipient = self.get_recipient(domain)

        # If no recipient from domain, check environment fallback
        if not recipient:
            recipient = os.getenv("CONTACT_RECEIVER") or self.smtp_user

        if not recipient:
            print("No contact receiver configured; skipping contact email.")
            return False

        msg = MIMEMultipart()
        msg["From"] = self.smtp_user or "no-reply@example.com"
        msg["To"] = recipient
        msg["Subject"] = f"Website Contact Form: {contact.full_name}"

        # Build a clean HTML table for the contact details
        origin_info = domain or getattr(contact, "origin_domain", "")
        html = f"""
        <html>
        <body>
        <h2>Contact Submission from {origin_info}</h2>
        <table border="1" cellpadding="6" cellspacing="0" style="border-collapse: collapse; font-family: Arial, sans-serif;">
          <tr><th align="left">Field</th><th align="left">Value</th></tr>
          <tr><td>Full name</td><td>{contact.full_name}</td></tr>
          <tr><td>Company</td><td>{getattr(contact, 'company', '')}</td></tr>
          <tr><td>Inquiry type</td><td>{getattr(contact, 'inquiry_type', '')}</td></tr>
          <tr><td>Email</td><td>{getattr(contact, 'email', '')}</td></tr>
          <tr><td>Message</td><td>{getattr(contact, 'message', '')}</td></tr>
          <tr><td>Origin domain</td><td>{origin_info}</td></tr>
        </table>
        </body>
        </html>
        """

        msg.attach(MIMEText(html, "html"))

        sent = self._send_smtp_message(msg, [recipient])
        if sent:
            print(f"✅ Contact email sent to {recipient}")
        else:
            print(f"Failed to send contact email to {recipient}")
        return sent

email_service = EmailService()
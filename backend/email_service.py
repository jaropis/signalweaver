"""Email service for authentication."""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import AuthConfig
from exceptions import EmailSendError

class EmailService:
    """Sends verification and notification emails via SMTP."""

    def __init__(self, config: AuthConfig):
        self.config = config

    def send_verification_email(self, email: str, token: str) -> bool:
        """
        send an email verification ling.

        The link points to the Vue app's verifictation page, which will extract the token from the URL and send it to the backend
        """
        if not self.config.mail_username or not self.config.mail_password:
            raise EmailSendError("Email credentials not configured")

        try:
            msg = MIMEMultipart()
            msg['From'] = self.config.mail_username
            msg['To'] = email
            msg['Subject'] = "Verify your account"

            # this URL points to the Vue app's /verify route
            verification_url = (
                f"{self.config.frontend_url}/verify?token={token}"
                )

            body= f"""
            Please click the link below to verify your email address:
            {verification_url}

            This link will expire in {self.config.verification_expires_hours} hours.

            If you didn't create this account, please ignore this email.
            """
            msg.attach(MIMEText(body, 'plain'))
            with smtplib.SMTP(
                    self.config.mail_server, self.config.mail_port) as server:
                if self.config.mail_use_tls:
                    server.starttls()
                server.login(self.config.mail_username, self.config.mail_password)
                server.send_message(msg)
            return True
        except Exception as e:
            raise EmailSendError(
                f"failed to send verification email: {str(e)}"
            )
                    
                

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class EmailService:
    @staticmethod
    def send_otp_email(to_email, otp_code):
        """Sends an OTP verification email to the user."""
        smtp_host = os.getenv('SMTP_HOST', 'smtp.gmail.com')
        smtp_port = int(os.getenv('SMTP_PORT', 587))
        smtp_email = os.getenv('SMTP_EMAIL', 'malikshoaib7983@gmail.com')
        smtp_password = os.getenv('SMTP_PASSWORD', '')

        # Fallback/Debug for local testing if password isn't set yet
        if not smtp_password or smtp_password == 'your_smtp_password':
            print(f"\n[DEV MODE] SMTP Password not configured. OTP for {to_email}: {otp_code}\n")
            return True, "OTP printed to terminal (Dev Mode)."

        subject = "HireFlow - Verification OTP"
        body = f"Your verification code for HireFlow is: {otp_code}\n\nThis code expires in 10 minutes."

        msg = MIMEMultipart()
        msg['From'] = smtp_email
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        try:
            with smtplib.SMTP(smtp_host, smtp_port) as server:
                server.starttls()
                server.login(smtp_email, smtp_password)
                server.sendmail(smtp_email, to_email, msg.as_string())
            return True, "OTP sent successfully."
        except Exception as e:
            # If email fails, print it to terminal as a fallback so testing doesn't break
            print(f"\n[SMTP ERROR] Failed to send email: {e}")
            print(f"[FALLBACK] OTP for {to_email}: {otp_code}\n")
            return False, str(e)
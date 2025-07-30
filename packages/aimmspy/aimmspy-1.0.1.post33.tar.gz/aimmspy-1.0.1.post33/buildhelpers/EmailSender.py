
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class EmailSender:
    def __init__(self, from_email, from_password, smtp_server, smtp_port):
        self.from_email = from_email
        self.from_password = from_password
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port

    def __init__(self, from_email):
        self.from_email = from_email

    def send_email(self, subject, body, to_emails):
        msg = MIMEMultipart()
        msg['From'] = self.from_email
        msg['To'] = ", ".join(to_emails)
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        try:
            server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port)
            server.login(self.from_email, self.from_password)
            server.sendmail(self.from_email, to_emails, msg.as_string())
            server.quit()
            print("Email sent successfully")
        except Exception as e:
            print(f"Failed to send email: {e}")

    def send_aimms_email(self, subject, body, to_emails):
        msg = MIMEMultipart()
        msg['From'] = self.from_email
        msg['To'] = ", ".join(to_emails)
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        try:
            server = smtplib.SMTP("smtp.intra.aimms.com")
            server.set_debuglevel(1)
            server.sendmail(self.from_email, to_emails, msg.as_string())
            server.quit()
            print("Email sent successfully")
        except Exception as e:
            print(f"Failed to send email: {e}")

    def test_send_email(self, subject, body, to_emails):
        msg = MIMEMultipart()
        msg['From'] = self.from_email
        msg['To'] = ", ".join(to_emails)
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        try:
            server = smtplib.SMTP('localhost', 1025)
            server.sendmail(self.from_email, to_emails, msg.as_string())
            server.quit()
            print("Test email sent successfully")
        except Exception as e:
            print(f"Failed to send test email: {e}")

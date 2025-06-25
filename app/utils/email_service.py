import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
from flask import current_app, render_template

class EmailService:
    def __init__(self):
        # Email configuration - make these attributes accessible
        self.smtp_server = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.environ.get('SMTP_PORT', 587))
        self.email_address = os.environ.get('EMAIL_ADDRESS', 'your_email@gmail.com')
        self.email_password = os.environ.get('EMAIL_PASSWORD', 'your_app_password')
    
    def test_connection(self):
        """Test SMTP connection"""
        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_address, self.email_password)
            return True, "Connection successful"
        except Exception as e:
            return False, str(e)
    
    def send_application_email(self, to_email, learnership, user):
        """Send application email with resume attachment"""
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = f"{user.name} <{self.email_address}>"
            msg['To'] = to_email
            msg['Reply-To'] = user.email
            msg['Subject'] = f"Application for {learnership['program']} - {user.name}"
            
            # Email body
            html_body = render_template('emails/application.html', 
                                      learnership=learnership, 
                                      user=user)
            msg.attach(MIMEText(html_body, 'html'))
            
            # Attach resume if available (using resume_file instead of resume_filename)
            if hasattr(user, 'resume_file') and user.resume_file:
                resume_path = os.path.join(current_app.root_path, 'static', 'resumes', user.resume_file)
                if os.path.exists(resume_path):
                    with open(resume_path, "rb") as attachment:
                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload(attachment.read())
                        encoders.encode_base64(part)
                        part.add_header(
                            'Content-Disposition',
                            f'attachment; filename= {user.resume_file}'
                        )
                        msg.attach(part)
                else:
                    print(f"Resume file not found at: {resume_path}")
            else:
                print(f"User {user.email} has no resume file attached")
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_address, self.email_password)
                server.send_message(msg)
            
            print(f"Email sent successfully to {to_email} for {learnership['program']}")
            return True
            
        except Exception as e:
            print(f"Error sending email to {to_email}: {str(e)}")
            return False
    
    def send_test_email(self, to_email):
        """Send a test email"""
        try:
            msg = MIMEText("This is a test email from Bulk Email App. Your email configuration is working correctly!")
            msg['Subject'] = "Test Email - Bulk Email App"
            msg['From'] = self.email_address
            msg['To'] = to_email
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_address, self.email_password)
                server.send_message(msg)
            
            return True
        except Exception as e:
            print(f"Error: {str(e)}")
            return False
    
    def send_batch_summary(self, user_email, batch_results):
        """Send a summary email after batch processing"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_address
            msg['To'] = user_email
            msg['Subject'] = "Batch Application Summary - Bulk Email App"
            
            # Create summary body
            success_count = sum(1 for r in batch_results if r.get('status') == 'success')
            failed_count = len(batch_results) - success_count
            
            html_body = f"""
            <html>
                <body>
                    <h2>Batch Application Summary</h2>
                    <p>Your batch application process has been completed.</p>
                    
                    <h3>Results:</h3>
                    <ul>
                        <li>Total Applications: {len(batch_results)}</li>
                        <li>Successful: {success_count}</li>
                        <li>Failed: {failed_count}</li>
                    </ul>
                    
                    <h3>Details:</h3>
                    <table border="1" cellpadding="5">
                        <tr>
                            <th>Company</th>
                            <th>Program</th>
                            <th>Status</th>
                            <th>Message</th>
                        </tr>
            """
            
            for result in batch_results:
                status_color = "green" if result.get('status') == 'success' else "red"
                html_body += f"""
                        <tr>
                            <td>{result.get('company', 'Unknown')}</td>
                            <td>{result.get('learnership', 'Unknown')}</td>
                            <td style="color: {status_color}">{result.get('status', 'Unknown')}</td>
                            <td>{result.get('message', '')}</td>
                        </tr>
                """
            
            html_body += """
                    </table>
                    <p>Best regards,<br>Bulk Email App Team</p>
                </body>
            </html>
            """
            
            msg.attach(MIMEText(html_body, 'html'))
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_address, self.email_password)
                server.send_message(msg)
            
            return True
            
        except Exception as e:
            print(f"Error sending summary email: {str(e)}")
            return False
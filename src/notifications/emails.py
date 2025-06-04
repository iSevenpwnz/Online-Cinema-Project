import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import aiosmtplib
from jinja2 import Environment, FileSystemLoader

from exceptions import BaseEmailError
from notifications.interfaces import EmailSenderInterface


class EmailSender(EmailSenderInterface):

    def __init__(
        self,
        hostname: str,
        port: int,
        email: str,
        password: str,
        use_tls: bool,
        template_dir: str,
        activation_email_template_name: str,
        activation_complete_email_template_name: str,
        password_email_template_name: str,
        password_complete_email_template_name: str,
    ):
        """
        Initializes the EmailSender with SMTP server settings and email template configuration.
        
        Args:
            hostname: SMTP server hostname.
            port: SMTP server port.
            email: Sender email address used for authentication.
            password: Password for the sender email account.
            use_tls: Whether to use TLS for the SMTP connection.
            template_dir: Directory containing Jinja2 email templates.
            activation_email_template_name: Filename of the account activation email template.
            activation_complete_email_template_name: Filename of the activation completion email template.
            password_email_template_name: Filename of the password reset request email template.
            password_complete_email_template_name: Filename of the password reset completion email template.
        """
        self._hostname = hostname
        self._port = port
        self._email = email
        self._password = password
        self._use_tls = use_tls
        self._activation_email_template_name = activation_email_template_name
        self._activation_complete_email_template_name = activation_complete_email_template_name
        self._password_email_template_name = password_email_template_name
        self._password_complete_email_template_name = password_complete_email_template_name

        self._env = Environment(loader=FileSystemLoader(template_dir))

    async def _send_email(self, recipient: str, subject: str, html_content: str) -> None:
        """
        Asynchronously sends an HTML email to the specified recipient with the given subject.
        
        Raises:
            BaseEmailError: If sending the email fails due to an SMTP error.
        """
        message = MIMEMultipart()
        message["From"] = self._email
        message["To"] = recipient
        message["Subject"] = subject
        message.attach(MIMEText(html_content, "html"))

        try:
            smtp = aiosmtplib.SMTP(hostname=self._hostname, port=self._port, start_tls=self._use_tls)
            await smtp.connect()
            if self._use_tls:
                await smtp.starttls()
            await smtp.login(self._email, self._password)
            await smtp.sendmail(self._email, [recipient], message.as_string())
            await smtp.quit()
        except aiosmtplib.SMTPException as error:
            logging.error(f"Failed to send email to {recipient}: {error}")
            raise BaseEmailError(f"Failed to send email to {recipient}: {error}")

    async def send_activation_email(self, email: str, activation_link: str) -> None:
        """
        Sends an account activation email with a personalized activation link asynchronously.
        
        Args:
            email: Recipient's email address.
            activation_link: URL for account activation to be included in the email.
        """
        template = self._env.get_template(self._activation_email_template_name)
        html_content = template.render(email=email, activation_link=activation_link)
        subject = "Account Activation"
        await self._send_email(email, subject, html_content)

    async def send_activation_complete_email(self, email: str, login_link: str) -> None:
        """
        Sends an account activation completion email with a login link asynchronously.
        
        The email is rendered from a template and sent to the specified recipient after successful account activation.
        """
        template = self._env.get_template(self._activation_complete_email_template_name)
        html_content = template.render(email=email, login_link=login_link)
        subject = "Account Activated Successfully"
        await self._send_email(email, subject, html_content)

    async def send_password_reset_email(self, email: str, reset_link: str) -> None:
        """
        Sends a password reset request email with a reset link asynchronously.
        
        Args:
            email: Recipient's email address.
            reset_link: URL for resetting the password to include in the email.
        """
        template = self._env.get_template(self._password_email_template_name)
        html_content = template.render(email=email, reset_link=reset_link)
        subject = "Password Reset Request"
        await self._send_email(email, subject, html_content)

    async def send_password_reset_complete_email(self, email: str, login_link: str) -> None:
        """
        Sends a password reset completion email asynchronously to the specified recipient.
        
        The email includes a login link and uses a pre-defined HTML template rendered with the recipient's email and login link.
        """
        template = self._env.get_template(self._password_complete_email_template_name)
        html_content = template.render(email=email, login_link=login_link)
        subject = "Your Password Has Been Successfully Reset"
        await self._send_email(email, subject, html_content)

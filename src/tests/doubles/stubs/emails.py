from notifications import EmailSenderInterface


class StubEmailSender(EmailSenderInterface):

    async def send_activation_email(self, email: str, activation_link: str) -> None:
        """
        Stub method for simulating the sending of an activation email.
        
        This method accepts the recipient's email address and an activation link but performs no action, serving as a placeholder for testing.
        """
        return None

    async def send_activation_complete_email(self, email: str, login_link: str) -> None:
        """
        Stub method for simulating the sending of an account activation completion email.
        
        This method accepts the recipient's email address and a login link but performs no action and returns immediately. Intended for use in testing environments where actual email delivery is not required.
        """
        return None

    async def send_password_reset_email(self, email: str, reset_link: str) -> None:
        """
        Stub method for sending a password reset email.
        
        This method simulates sending a password reset email to the specified address with the provided reset link, but performs no actual action.
        """
        return None

    async def send_password_reset_complete_email(self, email: str, login_link: str) -> None:
        """
        Stub method for simulating the sending of a password reset completion email.
        
        This method accepts the recipient's email address and a login link but performs no action and returns immediately. Intended for use in testing environments where actual email delivery is not required.
        """
        return None

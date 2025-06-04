from notifications import EmailSenderInterface


class StubEmailSender(EmailSenderInterface):

    async def send_activation_email(self, email: str, activation_link: str) -> None:
        """
        Stub method for sending an account activation email with an activation link.
        
        This method does not perform any action and is intended for use in testing environments.
        """
        return None

    async def send_activation_complete_email(self, email: str, login_link: str) -> None:
        """
        Stub method for sending an account activation completion email.
        
        Intended to simulate sending an email with a login link to the specified address. This method performs no action and is used for testing purposes.
        """
        return None

    async def send_password_reset_email(self, email: str, reset_link: str) -> None:
        """
        Stub method for sending a password reset email with a reset link.
        
        This method does not perform any action and is intended for use in testing environments.
        """
        return None

    async def send_password_reset_complete_email(self, email: str, login_link: str) -> None:
        """
        Stub method for sending a password reset completion email with a login link.
        
        Intended as a placeholder for testing; does not send any email or perform any action.
        """
        return None

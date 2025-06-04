from abc import ABC, abstractmethod


class EmailSenderInterface(ABC):

    @abstractmethod
    async def send_activation_email(self, email: str, activation_link: str) -> None:
        """
        Asynchronously sends an account activation email to the specified recipient.
        
        Args:
            email: The recipient's email address.
            activation_link: The activation link to include in the email.
        """
        pass

    @abstractmethod
    async def send_activation_complete_email(self, email: str, login_link: str) -> None:
        """
        Asynchronously sends an email confirming successful account activation.
        
        Args:
            email: Recipient's email address.
            login_link: Link for the user to log in after activation.
        """
        pass

    @abstractmethod
    async def send_password_reset_email(self, email: str, reset_link: str) -> None:
        """
        Asynchronously sends a password reset email to the specified recipient.
        
        Args:
            email: The recipient's email address.
            reset_link: The password reset link to include in the email.
        """
        pass

    @abstractmethod
    async def send_password_reset_complete_email(self, email: str, login_link: str) -> None:
        """
        Asynchronously sends a confirmation email indicating that the password reset process is complete.
        
        Args:
            email: The recipient's email address.
            login_link: The login link to include in the email.
        """
        pass

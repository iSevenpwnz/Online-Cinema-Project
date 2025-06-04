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
        Asynchronously sends an email confirming successful account activation to the specified recipient.
        
        Args:
            email: The recipient's email address.
            login_link: The login link to include in the email.
        """
        pass

    @abstractmethod
    async def send_password_reset_email(self, email: str, reset_link: str) -> None:
        """
        Asynchronously sends a password reset request email to the specified recipient.
        
        Args:
            email: Recipient's email address.
            reset_link: Link for resetting the password to be included in the email.
        """
        pass

    @abstractmethod
    async def send_password_reset_complete_email(self, email: str, login_link: str) -> None:
        """
        Asynchronously sends a password reset completion confirmation email to the specified recipient.
        
        Args:
            email: The recipient's email address.
            login_link: The login link to include in the email.
        """
        pass

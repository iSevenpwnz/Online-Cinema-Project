from abc import ABC, abstractmethod
from decimal import Decimal


class EmailSenderInterface(ABC):

    @abstractmethod
    async def send_activation_email(
        self, email: str, activation_link: str
    ) -> None:
        """
        Asynchronously send an account activation email.

        Args:
            email (str): The recipient's email address.
            activation_link (str): The activation link to include in the email.
        """
        pass

    @abstractmethod
    async def send_activation_complete_email(
        self, email: str, login_link: str
    ) -> None:
        """
        Asynchronously send an email confirming that the account has been activated.

        Args:
            email (str): The recipient's email address.
            login_link (str): The login link to include in the email.
        """
        pass

    @abstractmethod
    async def send_password_reset_email(
        self, email: str, reset_link: str
    ) -> None:
        """
        Asynchronously send a password reset request email.

        Args:
            email (str): The recipient's email address.
            reset_link (str): The password reset link to include in the email.
        """
        pass

    @abstractmethod
    async def send_password_reset_complete_email(
        self, email: str, login_link: str
    ) -> None:
        """
        Asynchronously send an email confirming that the password has been reset.

        Args:
            email (str): The recipient's email address.
            login_link (str): The login link to include in the email.
        """
        pass

    @abstractmethod
    async def send_success_payment_email(
        self,
        email: str,
        user_name: str,
        order_id: int,
        order_items: list,
        total_amount: Decimal,
    ):
        """
        Sends a success payment email to the specified user.
        Args:
            email (str): The recipient's email address.
            user_name (str): The name of the user who made the payment.
            order_id (int): The unique identifier of the order.
            order_items (list[OrderItem]): A list of items included in the order.
            total_amount (Decimal): The total amount paid for the order.
        # This method should construct and send an email notification to the user
        # confirming the successful payment of their order, including order details.
        """
        pass

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    @classmethod
    def default_order_by(cls):
        """
        Returns the default ordering criteria for queries on the model.
        
        Intended to be overridden by subclasses to specify a default ordering. By default, returns None, indicating no ordering is applied.
        """
        return None

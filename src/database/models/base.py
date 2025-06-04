from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    @classmethod
    def default_order_by(cls):
        """
        Returns the default ordering criterion for ORM queries.
        
        By default, this method returns None, indicating no ordering is specified. Subclasses can override this method to define a default order for query results.
        """
        return None

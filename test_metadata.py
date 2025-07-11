from app.db.base import Base
import app.models.user  # import the User model

print("Tables registered on Base.metadata:")
print(Base.metadata.tables.keys())

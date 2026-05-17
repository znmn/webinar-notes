from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.db.base import Base

DEFAULT_CATEGORY_NAMES = (
    "work",
    "personal",
    "finance",
    "learning",
    "other",
)


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)

    notes = relationship("Note", back_populates="category_rel")

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List

from db.base import Base

from db.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)

    name = Column(String)

    username = Column(String, unique=True)

    email = Column(String, unique=True)
    
    documents = Column(List[Document])

    password = Column(String)

    profile_picture = Column(String)

    description = Column(String)

    documents = relationship(
        "Document",
        back_populates="user",
       cascade="all, delete-orphan"
    )

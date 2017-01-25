from sqlalchemy import *
from sqlalchemy.orm import mapper, relation
from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import Integer, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID

from blogapp.model import DeclarativeBase, metadata, DBSession

class Post(DeclarativeBase):
    __tablename__ = 'post'

    id = Column(UUID, primary_key=True)
    title = Column(Text, unique=True)
    body = Column(Text)
    # author = Column(UUID, ForeignKey("user.user_id"), nullable=False)
    dateCreated = Column(DateTime, nullable=False)
    dateChanged = Column(DateTime)

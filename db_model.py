from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class MediaIds(Base):
    __tablename__ = 'media_ids'

    id = Column(Integer, primary_key=True)
    file_id = Column(String(255))
    filename = Column(String(255))


class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(255), unique=True, nullable=False)
    status = Column(Boolean, nullable=False)
    date = Column(DateTime, nullable=False, server_default=func.now())

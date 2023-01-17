from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class Menu(Base):
    __tablename__ = "menu"
    metadata
    id = Column(String, primary_key=True, index=True)
    title = Column(String(100), unique=True, nullable=False)
    description = Column(String(500))
    submenus_count = Column(Integer)
    dishes_count = Column(Integer)

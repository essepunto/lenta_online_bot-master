from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

import config

Base = declarative_base()


class UserSection(Base):
    __tablename__ = 'user_sections'
    id = Column(Integer, primary_key=True)
    section_name = Column(String(255), nullable=False)


class SkuToSection(Base):
    __tablename__ = 'sku_to_section'
    sku = Column(String, primary_key=True)
    section_name = Column(String)


class User(Base):
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True)
    first_name = Column(String(255))
    is_work = Column(Boolean, default=True)
    username = Column(String)


class UserSectionAssociation(Base):
    __tablename__ = 'user_section_association'
    user_id = Column(Integer, ForeignKey('users.user_id'), primary_key=True)
    user_section_id = Column(Integer, ForeignKey('user_sections.id'), primary_key=True)
    user = relationship("User", back_populates="user_section_associations")
    user_section = relationship("UserSection", back_populates="user_section_associations")


User.user_section_associations = relationship("UserSectionAssociation", back_populates="user")
UserSection.user_section_associations = relationship("UserSectionAssociation", back_populates="user_section")

# Создайте движок для подключения к базе данных
engine = create_engine(config.PG_DSN)
Base.metadata.create_all(engine)


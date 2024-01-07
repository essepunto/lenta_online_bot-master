from sqlalchemy import create_engine, Column, BigInteger, String, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
import pandas as pd
import config

Base = declarative_base()

class UserSection(Base):
    __tablename__ = 'user_sections'
    __table_args__ = {'extend_existing': True}
    id = Column(BigInteger ,primary_key=True)
    section_name = Column(String(255), nullable=False)
    user_associations = relationship("UserSectionAssociation", back_populates="user_section", cascade="all, delete-orphan")


class User(Base):
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}
    user_id = Column(BigInteger, primary_key=True)
    first_name = Column(String(255))
    is_work = Column(Boolean, default=True)
    username = Column(String)
    # Добавляем связь с UserSectionAssociation с каскадным удалением
    user_sections = relationship("UserSectionAssociation", back_populates="user", cascade="all, delete-orphan")

class SkuToSection(Base):
    __tablename__ = 'sku_to_section'
    sku = Column(String, primary_key=True)
    section_name = Column(String)

class UserSectionAssociation(Base):
    __tablename__ = 'user_section_association'
    user_id = Column(BigInteger, ForeignKey('users.user_id', ondelete='CASCADE'), primary_key=True)
    user_section_id = Column(BigInteger, ForeignKey('user_sections.id',ondelete='CASCADE'), primary_key=True)
    # Создание двусторонних связей с User и UserSection
    user = relationship("User", back_populates="user_sections")
    user_section = relationship("UserSection", back_populates="user_associations")

engine = create_engine(config.PG_DSN)

# Создание всех таблиц в базе данных
Base.metadata.create_all(engine)

# Настройка сессии для работы с базой данных
Session = sessionmaker(bind=engine)
session = Session()

# Чтение данных из CSV файла
csv_file_path = 'user_sections.csv'  # Укажите путь к файлу user_sections.csv
user_sections_df = pd.read_csv(csv_file_path)

# Добавление данных в таблицу user_sections
for _, row in user_sections_df.iterrows():
    section = UserSection(id=row['id'], section_name=row['section_name'])
    session.add(section)

# Фиксация транзакции
session.commit()

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Table, exists, create_engine
from sqlalchemy.exc import NoResultFound, SQLAlchemyError
from sqlalchemy.orm import declarative_base, relationship, sessionmaker, Session

import config

engine = create_engine(config.PG_DSN)
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine)

# Связующая таблица для отношения многие-ко-многим между User и UserSection
user_section_association = Table('user_section_association', Base.metadata,
                                 Column('user_id', Integer, ForeignKey('users.user_id')),
                                 Column('user_section_id', Integer, ForeignKey('user_sections.id'))
                                 )


# Модель пользователя
class User(Base):
    __tablename__ = 'users'

    user_id = Column(Integer, primary_key=True)
    username = Column(String)
    first_name = Column(String)
    is_work = Column(Boolean, default=True)
    user_sections = relationship("UserSection", secondary=user_section_association)

    def __repr__(self):
        return f"<User(user_id={self.user_id}, first_name='{self.first_name}', is_work='{self.is_work}')>"


# Модель секции пользователя
class UserSection(Base):
    __tablename__ = 'user_sections'

    id = Column(Integer, primary_key=True)
    section_name = Column(String, nullable=False)

    def __repr__(self):
        return f"<UserSection(id='{self.id}', section_name='{self.section_name}')>"


class SkuToSection(Base):
    __tablename__ = 'sku_to_section'

    sku = Column(String, primary_key=True)
    section_name = Column(String)

    def __repr__(self):
        return f"<SkuToSection(sku='{self.sku}', section_name='{self.section_name}')>"


# Функции для работы с базой данных
def create_user(user_id, first_name, user_section_names, is_work):
    db = SessionLocal()
    try:
        # Проверяем, существует ли уже пользователь
        user = db.query(User).filter_by(user_id=user_id).first()
        if not user:
            user = User(user_id=user_id, first_name=first_name, is_work=is_work)
            db.add(user)

        # Преобразуем список названий секций в уникальный набор
        unique_section_names = set(user_section_names)

        for name in unique_section_names:
            user_section = db.query(UserSection).filter_by(section_name=name).first()
            if user_section:
                # Проверяем, существует ли уже такая связь
                if not db.query(user_section_association).filter_by(
                        user_id=user_id, user_section_id=user_section.id).scalar():
                    # Добавляем связь, если она не существует
                    user.user_sections.append(user_section)

        db.commit()
    except SQLAlchemyError as e:
        print(f"Ошибка при создании пользователя: {e}")
        db.rollback()
    finally:
        db.close()


def is_user_registered(user_id):
    db = SessionLocal()
    user_exists = db.query(exists().where(User.user_id == user_id)).scalar()
    db.close()
    return user_exists


def get_section_by_sku(sku):
    db = SessionLocal()
    try:
        result = db.query(SkuToSection).filter(SkuToSection.sku == sku).first()
        if result:
            return result.section_name
        else:
            return None
    except SQLAlchemyError as e:
        print(f"Error getting section by SKU: {e}")
        return None
    finally:
        db.close()


def get_user_ids_by_section(section_name):
    db = SessionLocal()
    try:
        section = db.query(UserSection).filter(UserSection.section_name == section_name).one()
        user_ids = db.query(user_section_association.c.user_id).filter(
            user_section_association.c.user_section_id == section.id).all()
        return [user_id[0] for user_id in user_ids]
    except NoResultFound:
        return []
    except SQLAlchemyError as e:
        print(f"Error: {e}")
        return []
    finally:
        db.close()


def get_section_by_user_id(user_id):
    db = SessionLocal()
    try:
        sections = db.query(UserSection.section_name).join(user_section_association).filter(
            user_section_association.c.user_id == user_id).all()
        return [section[0] for section in sections]
    except NoResultFound:
        return []
    finally:
        db.close()


def get_user_info(user_id):
    db: Session = SessionLocal()
    try:
        # Получение пользователя по user_id
        user = db.query(User).filter(User.user_id == user_id).first()
        if user is not None:
            # Возвращаем словарь с информацией о пользователе
            return {
                "name": user.first_name,  # или user.name, в зависимости от вашей модели
                "status": "На работе" if user.is_work else "Дома"
            }
        else:
            return None
    except Exception as e:
        print(f"Ошибка при получении информации о пользователе: {e}")
        return None
    finally:
        db.close()


def get_username_by_id(user_id):
    db = SessionLocal()
    try:
        username = db.query(User.username).filter_by(user_id=user_id).scalar()
        return username
    except NoResultFound:
        pass
    finally:
        db.close()


def get_work_status_by_user_id(user_id):
    db = SessionLocal()
    try:
        status = db.query(User.is_work).filter_by(user_id=user_id).scalar()
        return status
    except NoResultFound:
        pass
    finally:
        db.close()


def update_work_status(user_id, new_status):
    db = SessionLocal()
    try:
        user = db.query(User).filter_by(user_id=user_id).first()
        if user:
            user.is_work = new_status
            db.commit()
    # Необходимо добавить обработку исключения здесь
    except SQLAlchemyError as e:
        print(f"Error updating work status: {e}")
        db.rollback()
    finally:
        db.close()


def remove_user_by_id(user_id):
    db = SessionLocal()
    try:
        # Поиск пользователя по user_id
        user = db.query(User).filter_by(user_id=user_id).first()
        if user:
            # Удаление пользователя, если он найден
            db.delete(user)
            db.commit()
            print(f"Пользователь с user_id {user_id} удален.")
        else:
            print(f"Пользователь с user_id {user_id} не найден.")
    except SQLAlchemyError as e:
        print(f"Ошибка при удалении пользователя: {e}")
        db.rollback()  # Откат изменений в случае ошибки
    finally:
        db.close()


# Создание всех таблиц
Base.metadata.create_all(engine)

if __name__ == "__main__":
    # Пример использования
    if not is_user_registered(12345):
        create_user(12345, 'Alex', ['Бакалея', 'Напитки'], True)

    print(get_section_by_user_id(12345))
    print(get_work_status_by_user_id(12345))

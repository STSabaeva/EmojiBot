import pathlib

from sqlalchemy import Column, ForeignKey, Integer, String, Text, DateTime, \
    create_engine
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Users(Base):
    __tablename__ = 'users'

    user_id = Column(
        Integer,
        nullable=False,
        unique=True,
        primary_key=True,
        autoincrement=True
    )
    user_name = Column(String(150), comment='Имя пользователя',
                       nullable=False, unique=True)

    def __init__(self, name):
        self.user_name = name

    def __repr__(self):
        return f'User(Name:{self.user_name}, user_id: {self.user_id}'


class Sessions(Base):
    __tablename__ = 'sessions'

    session_id = Column(
        Integer,
        nullable=False,
        unique=True,
        primary_key=True,
        autoincrement=True
    )
    start_time = Column(DateTime, comment='Время начала сессии', nullable=False)
    end_time = Column(DateTime, comment='Время окончания сессии',
                      nullable=False)

    def __init__(self, start_time, end_time):
        self.start_time = start_time
        self.end_time = end_time

    def __repr__(self):
        return f'Сессия: {self.session_id}. C {self.start_time} до {self.end_time}'


class Messages(Base):
    __tablename__ = 'messages'

    message_id = Column(
        Integer,
        nullable=False,
        unique=True,
        primary_key=True,
        autoincrement=True
    )
    user_id = Column(Integer, ForeignKey('users.user_id'),
                     comment='Номер пользователя')
    session_id = Column(Integer, ForeignKey('sessions.session_id'),
                        comment='Номер сессии')
    message_time = Column(DateTime, comment='Время написания сообщения',
                          nullable=False)
    text = Column(Text, comment='Текст сообщения')
    user = relationship('Users', backref='message_author', lazy='subquery')
    session = relationship('Sessions', backref='session of message',
                           lazy='subquery')

    def __init__(self, user_id, session_id, message_time, text):
        self.user_id = user_id
        self.session_id = session_id
        self.message_time = message_time
        self.text = text

    def __repr__(self):
        return f'Номер сообщения: {self.message_id}, номер пользователя: ' \
               f'{self.user_id}, номер сессии: {self.session_id}. ' \
               f'Время написания сообщения: {self.message_time}.' \
               f'Текст сообщения: {self.text}'


path = pathlib.Path(__file__).parent
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + \
                          str(path / "data" /
                              "fin_app.sqlite3?check_same_thread=False")
SQLALCHEMY_TRACK_MODIFICATIONS = False
SECRET_KEY = 'tatiana'

engine = create_engine(SQLALCHEMY_DATABASE_URI)
Base.metadata.create_all(engine)
Make_session = sessionmaker(bind=engine)
session = Make_session()

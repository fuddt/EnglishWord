from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Float
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime



Base = declarative_base()

class Word(Base):
    __tablename__ = 'words'
    id = Column(Integer, primary_key=True, autoincrement=True)
    word = Column(String, unique=True)
    meaning = Column(Text, default="")
    sentence = Column(Text, default="")
    last_reviewed = Column(DateTime, default=datetime.datetime.now())
    review_count = Column(Integer, default=0)
    difficulty = Column(Float, default=1.0)
    next_review = Column(DateTime, default=datetime.datetime.now())
    correct_count = Column(Integer, default=0)
    incorrect_count = Column(Integer, default=0)

DATABASE_URL = "sqlite:///words.db"
engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine)

def get_session():
    return SessionLocal()


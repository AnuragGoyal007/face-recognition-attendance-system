from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Date
from sqlalchemy.orm import relationship
from datetime import datetime, date
import pytz

from .database import Base

def get_ist_time():
    ist = pytz.timezone("Asia/Kolkata")
    return datetime.now(ist)

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    face_encoding = Column(String, nullable=False)


class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))

    lecture_slot = Column(String, nullable=False)

    date = Column(Date, default=date.today)
    timestamp = Column(DateTime, default=get_ist_time)
    latitude = Column(String)
    longitude = Column(String)

    student = relationship("Student")
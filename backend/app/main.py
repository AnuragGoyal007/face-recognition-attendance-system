from fastapi import FastAPI, UploadFile, File, Form, Depends
from sqlalchemy.orm import Session, joinedload
import shutil
import json
import numpy as np
import face_recognition
from fastapi.middleware.cors import CORSMiddleware

from datetime import date, datetime, time, timedelta
import pytz

from .database import engine, Base, SessionLocal
from .models import Student, Attendance
from .face_utils import encode_face
from .location_utils import is_within_radius


# =========================
# TIMEZONE CONFIG
# =========================

IST = pytz.timezone("Asia/Kolkata")


# =========================
# ADMIN CONFIG
# =========================

ADMIN_EMAIL = "admin@attendance.com"
ADMIN_PASSWORD = "admin123"


# =========================
# LECTURE SLOTS CONFIG
# =========================

LECTURE_SLOTS = [

    {
        "name": "JAVA",
        "start": time(16, 10),
        "end": time(17, 50)
    },

    {
        "name": "Lecture 2",
        "start": time(17, 50),
        "end": time(19, 30)
    },

    {
        "name": "Lecture 3",
        "start": time(19, 50),
        "end": time(21, 20)
    }

]

ALLOWED_MARKING_MINUTES = 10


# =========================
# FASTAPI INIT
# =========================

app = FastAPI(title="Attendance System API")


# =========================
# CORS
# =========================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================
# CREATE TABLES
# =========================

Base.metadata.create_all(bind=engine)


# =========================
# DATABASE DEPENDENCY
# =========================

def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


# =========================
# GET CURRENT LECTURE
# =========================

def get_current_lecture():

    now = datetime.now(IST).time()

    for lecture in LECTURE_SLOTS:

        start = lecture["start"]

        allowed_until = (
            datetime.combine(datetime.today(), start)
            + timedelta(minutes=ALLOWED_MARKING_MINUTES)
        ).time()

        if start <= now <= allowed_until:
            return lecture["name"]

    return None


# =========================
# ROOT
# =========================

@app.get("/")
def root():

    return {
        "message": "Attendance system running"
    }


# =========================
# STUDENT REGISTRATION
# =========================

@app.post("/register")
def register_student(
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    existing = db.query(Student).filter(
        Student.email == email
    ).first()

    if existing:

        return {
            "error": "Student already registered"
        }

    file_path = f"stored_faces/{email}.jpg"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    encoding = encode_face(file_path)

    if encoding is None:

        return {
            "error": "No face detected"
        }

    student = Student(

        name=name,
        email=email,
        password=password,
        face_encoding=json.dumps(encoding)

    )

    db.add(student)
    db.commit()

    return {
        "message": "Student registered successfully"
    }


# =========================
# STUDENT LOGIN
# =========================

@app.post("/student/login")
def student_login(

    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)

):

    student = db.query(Student).filter(
        Student.email == email
    ).first()

    if not student:

        return {
            "success": False,
            "message": "Student not found"
        }

    if student.password != password:

        return {
            "success": False,
            "message": "Incorrect password"
        }

    return {

        "success": True,
        "student_id": student.id,
        "name": student.name,
        "email": student.email

    }


# =========================
# MARK ATTENDANCE
# =========================

@app.post("/mark-attendance")
def mark_attendance(

    student_id: int = Form(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)

):

    # Save temp image

    temp_path = "stored_faces/temp.jpg"

    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)


    # Encode face

    unknown_encoding = encode_face(temp_path)

    if unknown_encoding is None:

        return {
            "error": "No face detected"
        }

    unknown_encoding = np.array(unknown_encoding)


    # Check lecture time window

    lecture_name = get_current_lecture()

    if not lecture_name:

        return {
            "error": "Attendance allowed only within first 10 minutes of lecture start"
        }

    print("Current lecture:", lecture_name)


    # Check location

    CLASS_LAT = 30.514683
    CLASS_LON = 76.6607895

    ALLOWED_RADIUS = 0.5


    if not is_within_radius(
        latitude,
        longitude,
        CLASS_LAT,
        CLASS_LON,
        ALLOWED_RADIUS
    ):

        return {

            "error": "You are not within allowed location",
            "your_latitude": latitude,
            "your_longitude": longitude

        }


    # Fetch logged in student

    student = db.query(Student).filter(
        Student.id == student_id
    ).first()

    if not student:

        return {
            "error": "Invalid student"
        }


    # Compare face

    known_encoding = np.array(
        json.loads(student.face_encoding)
    )

    distance = face_recognition.face_distance(
        [known_encoding],
        unknown_encoding
    )[0]


    print(f"Distance for {student.name}: {distance}")


    TOLERANCE = 0.45


    if distance > TOLERANCE:

        return {

            "error": "Face does not match logged in student",
            "confidence_distance": float(distance)

        }


    today = date.today()


    # Prevent duplicate per lecture

    existing = db.query(Attendance).filter(

        Attendance.student_id == student.id,
        Attendance.date == today,
        Attendance.lecture_slot == lecture_name

    ).first()


    if existing:

        return {

            "message": "Attendance already marked for this lecture",
            "student": student.name,
            "lecture": lecture_name

        }


    # Save attendance

    attendance = Attendance(

        student_id=student.id,
        lecture_slot=lecture_name,
        latitude=str(latitude),
        longitude=str(longitude)

    )


    db.add(attendance)
    db.commit()


    return {

        "message": "Attendance marked successfully",
        "student": student.name,
        "lecture": lecture_name,
        "confidence_distance": float(distance)

    }


# =========================
# ADMIN LOGIN
# =========================

@app.post("/admin/login")
def admin_login(

    email: str = Form(...),
    password: str = Form(...)

):

    if email == ADMIN_EMAIL and password == ADMIN_PASSWORD:

        return {
            "success": True,
            "message": "Admin login successful"
        }

    return {
        "success": False,
        "message": "Invalid credentials"
    }


# =========================
# ADMIN GET STUDENTS
# =========================

@app.get("/admin/students")
def get_students(
    db: Session = Depends(get_db)
):

    students = db.query(Student).all()

    result = []

    for s in students:

        result.append({

            "id": s.id,
            "name": s.name,
            "email": s.email

        })

    return result


# =========================
# ADMIN GET ATTENDANCE
# =========================

@app.get("/admin/attendance")
def get_attendance(
    db: Session = Depends(get_db)
):

    records = db.query(Attendance).options(
        joinedload(Attendance.student)
    ).all()

    result = []

    for r in records:

        result.append({

            "student": r.student.name,
            "email": r.student.email,
            "date": str(r.date),
            "time": str(r.timestamp),
            "lecture": r.lecture_slot,
            "latitude": r.latitude,
            "longitude": r.longitude

        })

    return result
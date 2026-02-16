from fastapi import FastAPI, UploadFile, File, Form, Depends
from sqlalchemy.orm import Session
import shutil
import os
import json
import numpy as np
from .models import Attendance
from .location_utils import is_within_radius
import face_recognition
from fastapi.middleware.cors import CORSMiddleware


from .database import engine, Base, SessionLocal
from .models import Student
from .face_utils import encode_face

app = FastAPI(title="Attendance System API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all origins (development only)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


Base.metadata.create_all(bind=engine)


# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def root():
    return {"message": "Attendance system running"}


@app.post("/register")
def register_student(
    name: str = Form(...),
    email: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    # Check if student already exists
    existing = db.query(Student).filter(Student.email == email).first()

    if existing:
        return {"error": "Student already registered"}

    # Save image
    file_path = f"stored_faces/{email}.jpg"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Encode face
    encoding = encode_face(file_path)

    if encoding is None:
        return {"error": "No face detected"}

    # Save to DB
    student = Student(
        name=name,
        email=email,
        face_encoding=json.dumps(encoding)
    )

    db.add(student)
    db.commit()

    return {"message": "Student registered successfully"}

@app.post("/mark-attendance")
def mark_attendance(
    latitude: float = Form(...),
    longitude: float = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    # Save temporary image
    temp_path = "stored_faces/temp.jpg"

    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Encode unknown face
    unknown_encoding = encode_face(temp_path)

    if unknown_encoding is None:
        return {"error": "No face detected"}

    unknown_encoding = np.array(unknown_encoding)

    # Classroom location
    CLASS_LAT = 30.7333
    CLASS_LON = 76.7794

    # Check location
    if not is_within_radius(latitude, longitude, CLASS_LAT, CLASS_LON):
        return {"error": "You are not within allowed location"}

    # Fetch all students
    students = db.query(Student).all()

    from datetime import date
    today = date.today()

    for student in students:

        known_encoding = np.array(json.loads(student.face_encoding))

        distance = face_recognition.face_distance(
            [known_encoding],
            unknown_encoding
        )[0]

        print(f"Distance for {student.name}: {distance}")

        TOLERANCE = 0.45

        if distance < TOLERANCE:

            # Check duplicate attendance
            existing = db.query(Attendance).filter(
                Attendance.student_id == student.id,
                Attendance.date == today
            ).first()

            if existing:
                return {
                    "message": "Attendance already marked today",
                    "student": student.name
                }

            # Mark attendance
            attendance = Attendance(
                student_id=student.id,
                latitude=str(latitude),
                longitude=str(longitude)
            )

            db.add(attendance)
            db.commit()

            return {
                "message": "Attendance marked successfully",
                "student": student.name,
                "confidence_distance": float(distance)
            }

    return {"error": "Face not recognized"}
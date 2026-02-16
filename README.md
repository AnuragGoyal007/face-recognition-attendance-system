# Face Recognition Attendance System

A web-based attendance system using face recognition and live camera capture.

## Tech Stack

Backend:
- FastAPI
- SQLAlchemy
- SQLite
- face_recognition
- OpenCV

Frontend:
- React (Vite)
- Axios
- Webcam capture

## Features

- Student registration using face image
- Live camera attendance marking
- Duplicate attendance prevention
- Face recognition with strict tolerance
- React frontend integration

## Run Backend

cd backend
venv\Scripts\activate
uvicorn app.main:app --reload

## Run Frontend

cd frontend
npm install
npm run dev
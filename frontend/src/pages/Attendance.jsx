import React, { useRef, useState } from "react";
import axios from "axios";
import "./Attendance.css";

function Attendance() {

  const videoRef = useRef(null);
  const canvasRef = useRef(null);

  const [cameraOn, setCameraOn] = useState(false);
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  // Start camera
  const startCamera = async () => {
    try {

      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: "user" } // ensures front camera on mobile
      });

      videoRef.current.srcObject = stream;
      setCameraOn(true);

    } catch (error) {
      console.error(error);
      setMessage("Camera access denied");
    }
  };

  // Capture and send image with GPS
  const markAttendance = async () => {

    if (!navigator.geolocation) {
      setMessage("GPS not supported on this device");
      return;
    }

    setLoading(true);
    setMessage("Getting location...");

    navigator.geolocation.getCurrentPosition(

      async (position) => {

        const latitude = position.coords.latitude;
        const longitude = position.coords.longitude;

        console.log("Location:", latitude, longitude);

        const canvas = canvasRef.current;
        const video = videoRef.current;

        if (!video.videoWidth) {
          setMessage("Camera not ready");
          setLoading(false);
          return;
        }

        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;

        const context = canvas.getContext("2d");
        context.drawImage(video, 0, 0);

        canvas.toBlob(async (blob) => {

          if (!blob) {
            setMessage("Image capture failed");
            setLoading(false);
            return;
          }

          const formData = new FormData();

          const student = JSON.parse(localStorage.getItem("student"));

          formData.append("student_id", student.student_id);
          formData.append("file", blob, "capture.jpg");
          formData.append("latitude", latitude);
          formData.append("longitude", longitude);

          try {

            setMessage("Processing attendance...");

            const response = await axios.post(
              "http://127.0.0.1:8000/mark-attendance",
              formData,
              {
                headers: {
                  "Content-Type": "multipart/form-data"
                }
              }
            );

            setMessage(JSON.stringify(response.data, null, 2));

          } catch (error) {

            console.error(error);

            if (error.response) {
              setMessage(JSON.stringify(error.response.data, null, 2));
            } else {
              setMessage("Server connection failed");
            }

          } finally {
            setLoading(false);
          }

        }, "image/jpeg");

      },

      (error) => {
        console.error(error);
        setMessage("Location permission denied");
        setLoading(false);
      },

      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 0
      }

    );

  };


  return (
  <div className="container">

    <h2 className="title">
      Face Recognition Attendance
    </h2>

    {!cameraOn &&
      <button className="button" onClick={startCamera}>
        Start Camera
      </button>
    }

    <br />

    <video
      ref={videoRef}
      autoPlay
      playsInline
      width="320"
      height="240"
      className="video"
    />

    <canvas
      ref={canvasRef}
      style={{ display: "none" }}
    />

    <br />

    {cameraOn &&
      <button
        className="button"
        onClick={markAttendance}
        disabled={loading}
      >
        {loading ? "Processing..." : "Mark Attendance"}
      </button>
    }

    <div className="message">
      {message}
    </div>

  </div>
);
}

export default Attendance;
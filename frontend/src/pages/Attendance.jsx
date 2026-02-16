import React, { useRef, useState } from "react";
import axios from "axios";

function Attendance() {

  const videoRef = useRef(null);
  const canvasRef = useRef(null);

  const [cameraOn, setCameraOn] = useState(false);
  const [message, setMessage] = useState("");

  // Start camera
  const startCamera = async () => {

    const stream = await navigator.mediaDevices.getUserMedia({
      video: true
    });

    videoRef.current.srcObject = stream;
    setCameraOn(true);
  };

  // Capture and send image
  const markAttendance = async () => {

    const canvas = canvasRef.current;
    const video = videoRef.current;

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    const context = canvas.getContext("2d");

    context.drawImage(video, 0, 0);

    canvas.toBlob(async (blob) => {

      const formData = new FormData();

      formData.append("file", blob, "capture.jpg");

      // Test coordinates (use your classroom coords)
      formData.append("latitude", 30.7333);
      formData.append("longitude", 76.7794);

      try {

        const response = await axios.post(
          "http://127.0.0.1:8000/mark-attendance",
          formData
        );

        setMessage(JSON.stringify(response.data));

      } catch (error) {

        setMessage("Error marking attendance");

      }

    }, "image/jpeg");

  };

  return (
    <div style={{ textAlign: "center" }}>

      <h1>Attendance System</h1>

      {!cameraOn &&
        <button onClick={startCamera}>
          Start Camera
        </button>
      }

      <br /><br />

      <video
        ref={videoRef}
        autoPlay
        width="400"
      />

      <canvas
        ref={canvasRef}
        style={{ display: "none" }}
      />

      <br /><br />

      {cameraOn &&
        <button onClick={markAttendance}>
          Mark Attendance
        </button>
      }

      <p>{message}</p>

    </div>
  );
}

export default Attendance;
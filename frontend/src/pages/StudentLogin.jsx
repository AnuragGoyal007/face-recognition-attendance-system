import React, { useState } from "react";
import axios from "axios";
import "./Attendance.css";

function StudentLogin({ onLoginSuccess }) {

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");

  const login = async () => {

    const formData = new FormData();

    formData.append("email", email);
    formData.append("password", password);

    try {

      const response = await axios.post(
        "http://127.0.0.1:8000/student/login",
        formData
      );

      if (response.data.success) {

        localStorage.setItem(
          "student",
          JSON.stringify(response.data)
        );

        onLoginSuccess(response.data);

      } else {

        setMessage(response.data.message);

      }

    } catch (error) {

      setMessage("Login failed");

    }

  };

  return (

    <div className="container">

      <h2>Student Login</h2>

      <input
        type="email"
        placeholder="Email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
      />

      <br /><br />

      <input
        type="password"
        placeholder="Password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />

      <br /><br />

      <button className="button" onClick={login}>
        Login
      </button>

      <p>{message}</p>

    </div>

  );
}

export default StudentLogin;
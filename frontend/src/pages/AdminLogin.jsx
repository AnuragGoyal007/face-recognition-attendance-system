import React, { useState } from "react";
import axios from "axios";
import "./Attendance.css";

function AdminLogin({ onLoginSuccess }) {

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");

  const login = async () => {

    const formData = new FormData();

    formData.append("email", email);
    formData.append("password", password);

    try {

      const response = await axios.post(
        "http://127.0.0.1:8000/admin/login",
        formData
      );

      if (response.data.success) {

        setMessage("Login successful");
        onLoginSuccess();

      } else {

        setMessage("Invalid credentials");

      }

    } catch (error) {

      setMessage("Login failed");

    }

  };

  return (

    <div className="container">

      <h2>Admin Login</h2>

      <input
        type="email"
        placeholder="Admin Email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        style={{ padding: "10px", margin: "10px" }}
      />

      <br />

      <input
        type="password"
        placeholder="Password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        style={{ padding: "10px", margin: "10px" }}
      />

      <br />

      <button className="button" onClick={login}>
        Login
      </button>

      <p>{message}</p>

    </div>

  );
}

export default AdminLogin;
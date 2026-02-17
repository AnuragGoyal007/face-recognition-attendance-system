import React, { useEffect, useState } from "react";
import axios from "axios";
import "./Attendance.css";

function AdminDashboard() {

  const [students, setStudents] = useState([]);
  const [attendance, setAttendance] = useState([]);

  useEffect(() => {

    fetchStudents();
    fetchAttendance();

  }, []);

  const fetchStudents = async () => {

    const response = await axios.get(
      "http://127.0.0.1:8000/admin/students"
    );

    setStudents(response.data);
  };

  const fetchAttendance = async () => {

    const response = await axios.get(
      "http://127.0.0.1:8000/admin/attendance"
    );

    setAttendance(response.data);
  };

  return (
    <div className="container">

      <h2>Admin Dashboard</h2>

      <h3>Registered Students</h3>

      <table border="1" width="100%">
        <thead>
          <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Email</th>
          </tr>
        </thead>

        <tbody>
          {students.map((student) => (
            <tr key={student.id}>
              <td>{student.id}</td>
              <td>{student.name}</td>
              <td>{student.email}</td>
            </tr>
          ))}
        </tbody>
      </table>

      <br />

      <h3>Attendance Records</h3>

      <table border="1" width="100%">
        <thead>
          <tr>
            <th>Name</th>
            <th>Email</th>
            <th>Date</th>
            <th>Time</th>
          </tr>
        </thead>

        <tbody>
          {attendance.map((record, index) => (
            <tr key={index}>
              <td>{record.student_name}</td>
              <td>{record.student_email}</td>
              <td>{record.date}</td>
              <td>{record.time}</td>
            </tr>
          ))}
        </tbody>

      </table>

    </div>
  );
}

export default AdminDashboard;
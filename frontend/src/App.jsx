import { useState, useEffect } from "react";

import Attendance from "./pages/Attendance";
import AdminDashboard from "./pages/AdminDashboard";
import AdminLogin from "./pages/AdminLogin";
import StudentLogin from "./pages/StudentLogin";

function App() {

  const [page, setPage] = useState("student");
  const [adminLoggedIn, setAdminLoggedIn] = useState(false);
  const [studentLoggedIn, setStudentLoggedIn] = useState(false);

  useEffect(() => {

    const student = localStorage.getItem("student");

    if (student) {
      setStudentLoggedIn(true);
    }

  }, []);

  const studentLogout = () => {

    localStorage.removeItem("student");
    setStudentLoggedIn(false);

  };

  return (

    <div style={{ textAlign: "center" }}>

      <div>

        <button onClick={() => setPage("student")}>
          Student
        </button>

        <button onClick={() => setPage("admin")}>
          Admin
        </button>

      </div>

      {page === "student" && !studentLoggedIn &&
        <StudentLogin
          onLoginSuccess={() => setStudentLoggedIn(true)}
        />
      }

      {page === "student" && studentLoggedIn &&
        <>
          <button onClick={studentLogout}>
            Logout
          </button>

          <Attendance />
        </>
      }

      {page === "admin" && !adminLoggedIn &&
        <AdminLogin
          onLoginSuccess={() => setAdminLoggedIn(true)}
        />
      }

      {page === "admin" && adminLoggedIn &&
        <AdminDashboard />
      }

    </div>

  );
}

export default App;
import React, {useEffect, useState} from 'react';
import GradeTable from '../webComponents/gradesTable';


function TeacherDashboard({user, onLogOut}) {
  const [courses, setCourses] = useState([]);
  const [currentCourse, setSCurrentCourse] = useState(null);
  const [students, setStudents] = useState([]);

  const fetchCourses = async () => {
    const teacherResponse = await fetch('/api/teacher/classes', { credentials: 'include' });
    const teacherData = await teacherResponse.json();

    setCourses(teacherData.classes || []);
  };

  useEffect(() => {
    fetchCourses();
  }, []);

  const selectCourse = async (courseId) => {
    setSCurrentCourse(courseId);
    const res = await fetch(`https://127.0.0.1:5000/teacher/course/${courseId}`);
    const data = await res.json();
    setStudents(data);
  };

  const updateGrade = async (studentId, grade) => {
    await fetch(`https://127.0.0.1:5000/teacher/course/${currentCourse}`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({student_id: studentId, grade: parseInt(grade)})
    });
    selectCourse(currentCourse);
  };

  return (
    <div>
      <h2>Welcome {user.name}!</h2>
      <button onClick={onLogOut}>Sign Out</button>
      <h3>Your Courses</h3>
      <ul>
        {courses.map(course => (
          <li key={course.id}>
            <button onClick={() => selectCourse(course.id)}>{course.name}</button>
          </li>
        ))}
      </ul>
      {currentCourse && (
        <div>
          <h3> Students and Grades</h3>
          <GradeTable students={students} onGradeChange={updateGrade} />
        </div>
      )}
    </div>
  );
}

export default TeacherDashboard
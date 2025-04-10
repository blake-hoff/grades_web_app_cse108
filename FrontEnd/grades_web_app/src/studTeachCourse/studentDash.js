import React, {useEffect, useState} from 'react';
import CourseTable from '../webComponents/courseTable';

function StudentDashboard({ user, onLogout }) {
  const [myCourses, setMyCourses] = useState([]);
  const [allCourses, setAllCourses] = useState([]);

  const fetchCourses = async () => {
    const myRes = await fetch(`http://127.0.0.1:5000/student/courses?user_id=${user.id}`);
    const allRes = await fetch(`http://127.0.0.1:5000/courses`);
    setMyCourses(await myRes.json());
    setAllCourses(await allRes.json());
  };

  useEffect(() => {
    fetchCourses();
  }, []);

  const enroll = async (id) => {
    await fetch(`http://127.0.0.1:5000/courses/enroll`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ student_id: user.id, course_id: id })
    });
    fetchCourses();
  };

  const unenroll = async (id) => {
    await fetch(`http://127.0.0.1:5000/courses/unenroll`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ student_id: user.id, course_id: id })
    });
    fetchCourses();
  };

  return (
    <div>
      <h2>Welcome {user.name}!</h2>
      <button onClick={onLogout}>Sign Out</button>
      <h3>Your Courses</h3>
      <CourseTable courses={myCourses} isStudent={false} />
      <h3>Available Courses</h3>
      <CourseTable courses={allCourses} onAdd={enroll} onRemove={unenroll} isStudent={true} />
    </div>
  );
}

export default StudentDashboard;
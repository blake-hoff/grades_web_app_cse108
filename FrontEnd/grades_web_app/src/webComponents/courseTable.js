import React from "react";

function CourseTable({courses, adding, removing, isStudent}) {
  return (
    <table className="course-table">
      <thead>
        <tr>
          <th>Name</th>
          <th>Teacher</th>
          <th>Time</th>
          <th>Enrolled</th>
          {isStudent && <th>Action</th>}
        </tr>
      </thead>
      <tbody> 
        {courses.map((course) =>
          <tr key = {course.id}>
            <td>{course.name}</td>
            <td>{course.teacher}</td>
            <td>{course.time}</td>
            <td>{course.enrolled}/{course.capacity}</td>
            {isStudent && (
              <td>
                {course.enrolled < course.capacity ? (
                  <button onClick={() => adding(course.id)}>➕</button>
                ) : (
                  <button onClick={() => removing(course.id)}>➖</button>
                )}
              </td>
            )}
          </tr>
        )}
      </tbody>
    </table>
  );
}

export default CourseTable;


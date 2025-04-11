import React from "react";

function CourseTable({courses, studentCourses = [], onAdd, onRemove, isStudent}) {
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
            <td>{course.class_name}</td>
            <td>{course.teacher_name}</td>
            <td>{course.course_time}</td>
            <td>{course.enrolled_count}/{course.capacity}</td>
            {isStudent && (
              <td>
                {course.enrolled_count < course.capacity ? (
                  <button onClick={() => onAdd(course.id)}>➕</button>
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


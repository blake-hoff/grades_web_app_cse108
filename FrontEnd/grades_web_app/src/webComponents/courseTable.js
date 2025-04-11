import React from "react";

function CourseTable({ courses, studentCourses = [], onAdd, onRemove, onEdit, isStudent }) {
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
        {courses.map((course) => {
          const isStudentEnrolled = studentCourses.some(c => c.id === course.id);

          return (
            <tr key={course.id}>
              <td>{course.class_name}
              {onEdit && (
                <button
                  className="view-students-button"
                  onClick={() => onEdit(course.id)}
                  title="View Students"
                >
                  👁️
                </button>
              )}
            </td>
              <td>{course.teacher_name}</td>
              <td>{course.course_time}</td>
              <td>{course.enrolled_count}/{course.capacity}</td>
              {isStudent && (
                <td>
                  {isStudentEnrolled ? (
                    <button onClick={() => onRemove(course.id)}>➖</button>
                  ) : (
                    <button
                      onClick={() => onAdd(course.id)}
                      disabled={course.enrolled_count >= course.capacity}
                    >
                      ➕
                    </button>
                  )}
                </td>
              )}
            </tr>
          );
        })}
      </tbody>
    </table>
  );
}


export default CourseTable;


import React from 'react';

function GradeTable({ students, onGradeChange }) {
  return (
    <table className="course-table">
      <thead>
        <tr>
          <th>Student Name</th>
          <th>Current Grade</th>
          <th>New Grade</th>
          <th>Action</th>
        </tr>
      </thead>
      <tbody>
        {students.map((student) => (
          <tr key={student.id}>
            <td>{student.first_name} {student.last_name}</td>
            <td>{student.grade ?? '—'}</td>
            <td>
              <input
                type="number"
                placeholder="Enter new grade"
                onChange={(e) => onGradeChange(student.id, e.target.value)}
              />
            </td>
            <td>
              <button>Save</button>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

export default GradeTable;
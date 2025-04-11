import React from 'react';

function GradeTable({ students, onGradeChange }) {
  return (
    <table className="course-table">
      <thead>
        <tr>
          <th>Student Name</th>
          <th>Grade</th>
        </tr>
      </thead>
      <tbody>
        {students.map((student) => (
          <tr key={student.id}>
            <td>{student.first_name} {student.last_name}</td>
            <td>
              <input
                type="number"
                value={student.grade || ''}
                onChange={(e) => onGradeChange(student.id, e.target.value)}
                style={{ width: '60px' }}
              />
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

export default GradeTable;
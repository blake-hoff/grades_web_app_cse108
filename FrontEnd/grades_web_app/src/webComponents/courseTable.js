<<<<<<< HEAD
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

      </tbody>
    </table>
  );
}
=======
>>>>>>> 49b8d353c157f41454bcd142d2713bbdc1570f89

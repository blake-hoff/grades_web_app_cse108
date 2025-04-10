
import React, {useState} from 'react';
import LoginPage from './webComponents/LoginPage';
import StudentDashboard from './studTeachCourse/studentDash';
import TeacherDashboard from './studTeachCourse/teachDash';

function App() {
  const [user, setUser] = useState(null);
  
  const handleLogin = (userData) => {
    setUser(userData);
  };

  const handleLogout = () => {
    setUser(null);
  };

  if (!user) return <LoginPage onLogin={handleLogin} />
  if (user.user_type === 'student') return <StudentDashboard user={user} onLogout={handleLogout} />;
  if (user.user_type === 'teacher') return <TeacherDashboard user={user} onLogout={handleLogout} />;

  return <div>Student {user.name} has an unknown role</div>; 
}

export default App;


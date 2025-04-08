<<<<<<< HEAD
import React, {useState, usestate} from 'react';
import LoginPage from './webComponents/LoginPage';
import studentDash from './studTeachCourse/studentDash';
import teachDash from './studTeachCourse/teachDash';

function App() {
  const [user, setUser] = useState(null);
  
  const handleLogin = (userData) => {
    setUser(userData);
  };

  const handleLogout = () => {
    setUser(null);
  };

  if (!user) return <LoginPage onLogin={handleLogin} />
  if (user.role === 'student') return <studentDash user={user} onLogout={handleLogout} />;
  if (user.role === 'teacher') return <teachDash user={user} onLogout={handleLogout} />;

  return <div>Unknown Role</div>; 
}

export default App;
=======
>>>>>>> 49b8d353c157f41454bcd142d2713bbdc1570f89

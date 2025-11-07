import './App.css';
import './CSS/style.css';
import Main from './components/main.jsx';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Login from './components/login.jsx';
import Register from './components/register.jsx';
import Header from './components/header.jsx';
import Footer from './components/footer.jsx';
import AuthProvider from './AuthProvider.jsx';
import PrivateRoute from './privateRoute.jsx';
import PublicRoute from './publicRoute.jsx';
import Attendance from './components/attendance.jsx';


function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Header />
        <Routes>
          <Route path='/' element={<Main />} />
          <Route path='/login' element={<PublicRoute><Login /></PublicRoute>} />
          <Route path='/register' element={<PublicRoute><Register /></PublicRoute>} />
          <Route path='/attendance' element={<PrivateRoute><Attendance /></PrivateRoute>} />
          <Route path='*' element={<Main />} />
          </Routes>
        <Footer />
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
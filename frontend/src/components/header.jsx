import React, { useContext } from 'react'
import Button from './button.jsx'
import { Link , useNavigate } from 'react-router-dom'
import { AuthContext } from '../AuthProvider.jsx'

const Header = () => {
  const { isLoggedIn, setIsLoggedIn } = useContext(AuthContext)
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    setIsLoggedIn(false)
    navigate('/login')
  }

  // ✅ Double-check: on ne considère connecté que si le contexte ET le token sont présents
  const authed = isLoggedIn && !!localStorage.getItem('access_token')

  return (
    <nav className="navbar container d-flex justify-content-between align-items-start pt-3 pb-3">
      <Link className="navbar-brand text-light mb-0 h1" to='/'>
        VDE Attendance Home
      </Link>

      <div className="d-flex align-items-center">
        {authed ? (
          <>
            <Button text="Attendance" class="btn-info" url="/attendance" />
            &nbsp;
            <button className='btn btn-danger' onClick={handleLogout}>Logout</button>
          </>
        ) : (
          <>
            <Button text="Login" class="btn-outline-info" url="/login" />
            <Button text="Register" class="btn-info" url="/register" />
          </>
        )}
      </div>
    </nav>
  )
}

export default Header
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function Navbar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  return (
    <nav className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16 items-center">
          <Link to="/" className="text-xl font-bold text-blue-600">HireMatch AI</Link>

          <div className="flex items-center gap-4">
            <Link to="/jobs" className="text-gray-600 hover:text-blue-600">Find Jobs</Link>

            {!user ? (
              <>
                <Link to="/login" className="text-gray-600 hover:text-blue-600">Login</Link>
                <Link to="/register" className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">Get Started</Link>
              </>
            ) : (
              <>
                {user.role === 'candidate' && (
                  <>
                    <Link to="/candidate/dashboard" className="text-gray-600 hover:text-blue-600">Dashboard</Link>
                    <Link to="/candidate/applications" className="text-gray-600 hover:text-blue-600">My Applications</Link>
                    <Link to="/candidate/profile" className="text-gray-600 hover:text-blue-600">Profile</Link>
                  </>
                )}
                {user.role === 'employer' && (
                  <>
                    <Link to="/employer/jobs" className="text-gray-600 hover:text-blue-600">My Jobs</Link>
                    <Link to="/employer/post-job" className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">Post Job</Link>
                  </>
                )}
                {user.role === 'admin' && (
                  <Link to="/admin" className="text-gray-600 hover:text-blue-600">Admin</Link>
                )}
                <button onClick={logout} className="text-gray-500 hover:text-red-600">Logout</button>
              </>
            )}
          </div>
        </div>
      </div>
    </nav>
  )
}

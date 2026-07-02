import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import api from '../api/client'
import { useAuth } from '../context/AuthContext'

export default function JobDetail() {
  const { id } = useParams()
  const { user } = useAuth()
  const navigate = useNavigate()
  const [job, setJob] = useState(null)
  const [applying, setApplying] = useState(false)

  useEffect(() => {
    api.get(`/jobs/${id}/`).then((res) => setJob(res.data)).catch(() => navigate('/jobs'))
  }, [id])

  const handleApply = async () => {
    if (!user) return navigate('/login')
    setApplying(true)
    try {
      await api.post(`/applications/jobs/${id}/apply/`)
      navigate('/candidate/applications')
    } catch (err) {
      alert(err.response?.data?.error || 'Application failed')
    } finally {
      setApplying(false)
    }
  }

  if (!job) return <div className="text-center py-20"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div></div>

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <div className="bg-white p-8 rounded-xl shadow-sm border border-gray-200">
        <h1 className="text-3xl font-bold mb-2">{job.title}</h1>
        <p className="text-gray-500 mb-6">{job.employer_name} · {job.location}</p>
        {job.salary_min && <p className="text-gray-700 mb-4">Salary: ${job.salary_min} - ${job.salary_max}</p>}
        {user?.role === 'candidate' && (
          <button onClick={handleApply} disabled={applying}
            className="bg-blue-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 mb-6">
            {applying ? 'Applying...' : 'Apply Now'}
          </button>
        )}
        <div className="prose max-w-none">
          <h3 className="text-lg font-semibold mt-6 mb-2">Job Description</h3>
          <p className="text-gray-700 whitespace-pre-wrap">{job.description}</p>
          {job.required_skills && (
            <>
              <h3 className="text-lg font-semibold mt-6 mb-2">Required Skills</h3>
              <div className="flex flex-wrap gap-2">
                {job.required_skills.split(',').map((s) => (
                  <span key={s} className="bg-blue-50 text-blue-700 px-3 py-1 rounded-full text-sm">{s.trim()}</span>
                ))}
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  )
}

import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import api from '../api/client'

export default function ManageJobs() {
  const [jobs, setJobs] = useState([])
  const [stats, setStats] = useState({ total: 0, open: 0, totalApps: 0 })

  useEffect(() => {
    api.get('/jobs/mine/').then((res) => {
      const list = res.data.results || res.data
      setJobs(list)
      setStats({
        total: list.length,
        open: list.filter((j) => j.status === 'open').length,
        totalApps: list.reduce((s, j) => s + (j.applications_count || 0), 0),
      })
    }).catch(console.error)
  }, [])

  const toggleStatus = async (job) => {
    const newStatus = job.status === 'open' ? 'closed' : 'open'
    await api.put(`/jobs/${job.id}/`, { status: newStatus })
    setJobs(jobs.map((j) => j.id === job.id ? { ...j, status: newStatus } : j))
  }

  return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">My Jobs</h1>
        <Link to="/employer/post-job" className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">+ Post New Job</Link>
      </div>

      <div className="grid grid-cols-3 gap-4 mb-8">
        <div className="bg-white p-4 rounded-xl shadow-sm border text-center">
          <div className="text-2xl font-bold text-blue-600">{stats.total}</div>
          <div className="text-gray-500 text-sm">Total Jobs</div>
        </div>
        <div className="bg-white p-4 rounded-xl shadow-sm border text-center">
          <div className="text-2xl font-bold text-green-600">{stats.open}</div>
          <div className="text-gray-500 text-sm">Open</div>
        </div>
        <div className="bg-white p-4 rounded-xl shadow-sm border text-center">
          <div className="text-2xl font-bold text-purple-600">{stats.totalApps}</div>
          <div className="text-gray-500 text-sm">Total Applicants</div>
        </div>
      </div>

      {jobs.length === 0 ? (
        <div className="text-center py-12 text-gray-500">No jobs posted yet</div>
      ) : (
        <div className="space-y-4">
          {jobs.map((job) => (
            <div key={job.id} className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 flex justify-between items-center">
              <div>
                <h3 className="text-lg font-semibold">{job.title}</h3>
                <p className="text-gray-500 text-sm">
                  {job.location} · {job.applications_count || 0} applicant{(job.applications_count || 0) !== 1 ? 's' : ''}
                  {job.salary_min && ` · $${job.salary_min} - $${job.salary_max}`}
                </p>
                <span className={`inline-block mt-2 px-2 py-1 rounded text-xs font-medium ${job.status === 'open' ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'}`}>{job.status}</span>
              </div>
              <div className="flex gap-3 items-center">
                {job.applications_count > 0 && (
                  <Link to={`/employer/jobs/${job.id}/applicants`}
                    className="bg-blue-50 text-blue-600 px-3 py-1.5 rounded-lg text-sm hover:bg-blue-100">
                    View {job.applications_count} Applicant{(job.applications_count || 0) !== 1 ? 's' : ''}
                  </Link>
                )}
                <button onClick={() => toggleStatus(job)}
                  className="text-gray-500 hover:text-gray-700 text-sm border px-3 py-1.5 rounded-lg">
                  {job.status === 'open' ? 'Close' : 'Reopen'}
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

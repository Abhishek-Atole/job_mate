import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import api from '../api/client'

export default function JobList() {
  const [jobs, setJobs] = useState([])
  const [search, setSearch] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.get('/jobs/', { params: { search } })
      .then((res) => setJobs(res.data.results || res.data))
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [search])

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">Find Jobs</h1>
      <input type="text" placeholder="Search by title, skills, or location..." value={search}
        onChange={(e) => setSearch(e.target.value)}
        className="w-full px-4 py-3 border border-gray-300 rounded-lg mb-8 focus:ring-2 focus:ring-blue-500 outline-none" />
      
      {loading ? (
        <div className="text-center py-12"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div></div>
      ) : jobs.length === 0 ? (
        <div className="text-center py-12 text-gray-500">No jobs found</div>
      ) : (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {jobs.map((job) => (
            <Link key={job.id} to={`/jobs/${job.id}`} className="block bg-white p-6 rounded-xl shadow-sm border border-gray-200 hover:shadow-md transition">
              <h3 className="text-lg font-semibold text-gray-900 mb-2">{job.title}</h3>
              <p className="text-gray-500 text-sm mb-2">{job.employer_name} · {job.location}</p>
              {job.salary_min && <p className="text-gray-600 text-sm mb-3">${job.salary_min} - ${job.salary_max}</p>}
              {job.required_skills && (
                <div className="flex flex-wrap gap-2">
                  {job.required_skills.split(',').slice(0, 4).map((s) => (
                    <span key={s} className="bg-gray-100 text-gray-600 px-2 py-1 rounded text-xs">{s.trim()}</span>
                  ))}
                </div>
              )}
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}

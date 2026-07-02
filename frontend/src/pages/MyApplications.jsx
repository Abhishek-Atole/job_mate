import { useState, useEffect } from 'react'
import api from '../api/client'

export default function MyApplications() {
  const [applications, setApplications] = useState([])

  useEffect(() => {
    api.get('/applications/me/').then((res) => setApplications(res.data.results || res.data)).catch(console.error)
  }, [])

  const statusColors = {
    applied: 'bg-blue-100 text-blue-700',
    shortlisted: 'bg-green-100 text-green-700',
    rejected: 'bg-red-100 text-red-700',
    hired: 'bg-purple-100 text-purple-700',
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">My Applications</h1>
      {applications.length === 0 ? (
        <div className="text-center py-12 text-gray-500">No applications yet. <a href="/jobs" className="text-blue-600 hover:underline">Browse jobs</a></div>
      ) : (
        <div className="space-y-4">
          {applications.map((app) => (
            <div key={app.id} className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
              <div className="flex justify-between items-center">
                <div>
                  <h3 className="text-lg font-semibold">{app.job_title}</h3>
                  <p className="text-gray-500 text-sm">Applied {new Date(app.applied_at).toLocaleDateString()}</p>
                </div>
                <div className="text-right">
                  {app.match_score !== null && <div className="text-lg font-bold text-blue-600">{app.match_score}% match</div>}
                  <span className={`inline-block mt-1 px-3 py-1 rounded-full text-xs font-medium ${statusColors[app.status]}`}>{app.status}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

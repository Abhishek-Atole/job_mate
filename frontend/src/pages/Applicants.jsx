import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import api from '../api/client'

export default function Applicants() {
  const { id } = useParams()
  const [applications, setApplications] = useState([])
  const [jobTitle, setJobTitle] = useState('')

  useEffect(() => {
    api.get(`/applications/jobs/${id}/applications/`).then((res) => {
      setApplications(res.data.results || res.data)
      if (res.data.results?.[0]?.job_title) setJobTitle(res.data.results[0].job_title)
    }).catch(console.error)
    api.get(`/jobs/${id}/`).then((res) => setJobTitle(res.data.title)).catch(() => {})
  }, [id])

  const updateStatus = async (appId, status) => {
    await api.put(`/applications/${appId}/status/`, { status })
    setApplications(applications.map((a) => a.id === appId ? { ...a, status } : a))
  }

  const getScoreColor = (score) => {
    if (score >= 70) return 'bg-green-500'
    if (score >= 40) return 'bg-yellow-500'
    return 'bg-red-500'
  }

  return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-2">{jobTitle || 'Applicants'}</h1>
      <p className="text-gray-500 mb-6">{applications.length} applicants · Ranked by match score</p>
      {applications.length === 0 ? (
        <div className="text-center py-12 text-gray-500">No applications yet</div>
      ) : (
        <div className="space-y-3">
          {applications.map((app, i) => (
            <div key={app.id} className="bg-white p-5 rounded-xl shadow-sm border border-gray-200">
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <div className="flex items-center gap-3">
                    <span className="text-gray-400 font-medium">#{i + 1}</span>
                    <h3 className="font-semibold">{app.candidate_name || app.candidate_email}</h3>
                    <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                      app.status === 'applied' ? 'bg-blue-100 text-blue-700' :
                      app.status === 'shortlisted' ? 'bg-green-100 text-green-700' :
                      app.status === 'rejected' ? 'bg-red-100 text-red-700' :
                      'bg-purple-100 text-purple-700'
                    }`}>{app.status}</span>
                  </div>
                  {app.candidate_skills && <p className="text-gray-500 text-sm mt-1">{app.candidate_skills}</p>}
                  {app.candidate_experience > 0 && <p className="text-gray-500 text-sm">{app.candidate_experience} years experience</p>}
                </div>
                <div className="text-right">
                  {app.match_score !== null && (
                    <div className="mb-2">
                      <div className="text-2xl font-bold">{app.match_score}%</div>
                      <div className="w-24 h-2 bg-gray-200 rounded-full mt-1">
                        <div className={`h-full rounded-full ${getScoreColor(app.match_score)}`} style={{ width: `${app.match_score}%` }} />
                      </div>
                    </div>
                  )}
                  <div className="flex gap-2">
                    {app.status === 'applied' && (
                      <>
                        <button onClick={() => updateStatus(app.id, 'shortlisted')} className="text-sm text-green-600 hover:underline">Shortlist</button>
                        <button onClick={() => updateStatus(app.id, 'rejected')} className="text-sm text-red-600 hover:underline">Reject</button>
                      </>
                    )}
                    {app.status === 'shortlisted' && (
                      <button onClick={() => updateStatus(app.id, 'hired')} className="text-sm text-purple-600 hover:underline">Hire</button>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

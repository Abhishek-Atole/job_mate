import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import api from '../api/client'

function MatchBadge({ score }) {
  const s = parseFloat(score)
  const color = s >= 70 ? 'bg-green-100 text-green-700' : s >= 40 ? 'bg-yellow-100 text-yellow-700' : 'bg-red-100 text-red-700'
  return <span className={`px-2 py-1 rounded text-xs font-bold ${color}`}>{score}%</span>
}

export default function CandidateDashboard() {
  const [profile, setProfile] = useState(null)
  const [recommendations, setRecommendations] = useState([])
  const [loading, setLoading] = useState(true)
  const [applying, setApplying] = useState(false)
  const [applied, setApplied] = useState({})
  const [error, setError] = useState('')

  useEffect(() => {
    Promise.all([
      api.get('/candidates/me/'),
      api.get('/jobs/recommendations/'),
    ]).then(([profRes, recRes]) => {
      setProfile(profRes.data)
      setRecommendations(recRes.data)
    }).catch(() => setError('Failed to load. Fill your profile first.'))
      .finally(() => setLoading(false))
  }, [])

  const applyToJob = async (jobId) => {
    try {
      await api.post(`/applications/jobs/${jobId}/apply/`)
      setApplied((prev) => ({ ...prev, [jobId]: true }))
    } catch {
      setApplied((prev) => ({ ...prev, [jobId]: 'error' }))
    }
  }

  const autoApply = async () => {
    setApplying(true)
    const top = recommendations.slice(0, 5)
    for (const job of top) {
      if (!applied[job.id]) await applyToJob(job.id)
    }
    setApplying(false)
  }

  if (loading) {
    return (
      <div className="flex justify-center py-20">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">My Dashboard</h1>
        <Link to="/candidate/profile" className="text-blue-600 hover:underline text-sm">Edit Profile</Link>
      </div>

      {profile && (
        <div className="bg-white p-4 rounded-xl shadow-sm border mb-6">
          <p className="text-gray-600"><strong>Skills:</strong> {profile.skills || 'Not set'}</p>
          <p className="text-gray-600"><strong>Experience:</strong> {profile.experience_years} years</p>
          <p className="text-gray-600"><strong>Education:</strong> {profile.education || 'Not set'}</p>
        </div>
      )}

      {error && <div className="bg-red-50 text-red-600 p-4 rounded-lg mb-6">{error}</div>}

      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-semibold">Recommended Jobs</h2>
        {recommendations.length > 0 && (
          <button
            onClick={autoApply}
            disabled={applying}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-blue-700 disabled:opacity-50"
          >
            {applying ? 'Applying...' : 'Auto-Apply to Top 5'}
          </button>
        )}
      </div>

      {recommendations.length === 0 ? (
        <div className="text-center py-12 text-gray-500">
          No matching jobs found. Update your profile skills to get recommendations.
        </div>
      ) : (
        <div className="space-y-4">
          {recommendations.map((job) => (
            <div key={job.id} className="bg-white p-5 rounded-xl shadow-sm border flex justify-between items-center">
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-1">
                  <h3 className="text-lg font-semibold">{job.title}</h3>
                  <MatchBadge score={job.match_score} />
                </div>
                <p className="text-gray-500 text-sm">
                  {job.employer_name} · {job.location}
                  {job.salary_min && ` · $${job.salary_min} - $${job.salary_max}`}
                </p>
                {job.required_skills && (
                  <div className="flex flex-wrap gap-1 mt-2">
                    {job.required_skills.split(',').slice(0, 5).map((s) => (
                      <span key={s} className="bg-gray-100 text-gray-600 px-2 py-0.5 rounded text-xs">{s.trim()}</span>
                    ))}
                  </div>
                )}
              </div>
              <div className="ml-4">
                {applied[job.id] === true ? (
                  <span className="text-green-600 text-sm font-medium">Applied</span>
                ) : applied[job.id] === 'error' ? (
                  <span className="text-red-500 text-sm">Error</span>
                ) : (
                  <button
                    onClick={() => applyToJob(job.id)}
                    className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-blue-700"
                  >
                    Apply
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      <div className="mt-8 text-center">
        <Link to="/jobs" className="text-blue-600 hover:underline">Browse all jobs →</Link>
      </div>
    </div>
  )
}

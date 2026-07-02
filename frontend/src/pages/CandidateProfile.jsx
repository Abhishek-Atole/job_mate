import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../api/client'

export default function CandidateProfile() {
  const navigate = useNavigate()
  const [form, setForm] = useState({ skills: '', experience_years: 0, education: '', phone: '' })
  const [resumeFile, setResumeFile] = useState(null)
  const [resumeName, setResumeName] = useState('')
  const [extracting, setExtracting] = useState(false)
  const [extractedSkills, setExtractedSkills] = useState([])
  const [saved, setSaved] = useState(false)

  useEffect(() => {
    api.get('/candidates/me/').then((res) => {
      setForm({
        skills: res.data.skills || '',
        experience_years: res.data.experience_years || 0,
        education: res.data.education || '',
        phone: res.data.phone || '',
      })
    }).catch(() => {})
  }, [])

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value })

  const handleResumeSelect = async (e) => {
    const file = e.target.files[0]
    if (!file) return
    setResumeFile(file)
    setResumeName(file.name)
    setExtracting(true)
    const fd = new FormData()
    fd.append('resume_file', file)
    try {
      const res = await api.post('/candidates/extract-skills/', fd)
      setExtractedSkills(res.data.skills || [])
    } catch {
      setExtractedSkills([])
    }
    setExtracting(false)
  }

  const applyExtractedSkills = () => {
    if (extractedSkills.length === 0) return
    const existing = form.skills ? form.skills.split(',').map(s => s.trim()) : []
    const combined = [...new Set([...existing, ...extractedSkills])]
    setForm({ ...form, skills: combined.join(', ') })
    setExtractedSkills([])
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    const data = new FormData()
    Object.entries(form).forEach(([k, v]) => data.append(k, v))
    if (resumeFile) data.append('resume_file', resumeFile)
    await api.put('/candidates/me/', data, { headers: { 'Content-Type': 'multipart/form-data' } })
    setSaved(true)
    setTimeout(() => setSaved(false), 3000)
  }

  const skillPreview = form.skills.split(',').filter(Boolean)

  return (
    <div className="max-w-3xl mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">My Profile</h1>
      <form onSubmit={handleSubmit} className="bg-white p-8 rounded-xl shadow-sm border border-gray-200 space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Skills (comma separated)</label>
          <input type="text" name="skills" value={form.skills} onChange={handleChange}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none" />
          {skillPreview.length > 0 && (
            <div className="flex flex-wrap gap-1 mt-2">
              {skillPreview.map((s) => (
                <span key={s} className="bg-blue-50 text-blue-600 px-2 py-0.5 rounded text-xs">{s.trim()}</span>
              ))}
            </div>
          )}
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Years of Experience</label>
            <input type="number" name="experience_years" value={form.experience_years} onChange={handleChange}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Phone</label>
            <input type="text" name="phone" value={form.phone} onChange={handleChange}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none" />
          </div>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Education</label>
          <textarea name="education" rows={3} value={form.education} onChange={handleChange}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none" />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Resume (PDF)</label>
          <input type="file" accept=".pdf" onChange={handleResumeSelect}
            className="w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100" />
          {resumeName && <p className="text-xs text-gray-500 mt-1">Selected: {resumeName}</p>}
          {extracting && <p className="text-xs text-blue-500 mt-1">Extracting skills from resume...</p>}
          {extractedSkills.length > 0 && (
            <div className="mt-2 p-3 bg-blue-50 rounded-lg border border-blue-200">
              <p className="text-sm font-medium text-blue-700 mb-1">Extracted Skills ({extractedSkills.length} found)</p>
              <div className="flex flex-wrap gap-1 mb-2">
                {extractedSkills.map((s) => (
                  <span key={s} className="bg-white text-blue-600 px-2 py-0.5 rounded text-xs border border-blue-200">{s}</span>
                ))}
              </div>
              <button type="button" onClick={applyExtractedSkills}
                className="text-sm text-blue-600 hover:text-blue-800 font-medium">
                + Add all to skills
              </button>
            </div>
          )}
        </div>
        <div className="flex gap-4 items-center">
          <button type="submit" className="bg-blue-600 text-white px-6 py-2 rounded-lg font-medium hover:bg-blue-700">Save</button>
          {saved && <span className="text-green-600">Saved!</span>}
          <button type="button" onClick={() => navigate('/candidate/dashboard')}
            className="border border-blue-600 text-blue-600 px-6 py-2 rounded-lg font-medium hover:bg-blue-50">
            Find Matching Jobs
          </button>
        </div>
      </form>
    </div>
  )
}

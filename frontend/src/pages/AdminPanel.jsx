import { useState, useEffect } from 'react'
import api from '../api/client'

export default function AdminPanel() {
  const [stats, setStats] = useState(null)
  const [users, setUsers] = useState([])

  useEffect(() => {
    api.get('/admin/stats/').then((res) => setStats(res.data)).catch(console.error)
    api.get('/admin/users/').then((res) => setUsers(res.data.results || res.data)).catch(console.error)
  }, [])

  const toggleUser = async (userId) => {
    await api.put(`/admin/users/${userId}/toggle/`)
    setUsers(users.map((u) => u.id === userId ? { ...u, is_active: !u.is_active } : u))
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-8">Admin Panel</h1>
      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          {[
            { label: 'Total Users', value: stats.total_users },
            { label: 'Employers', value: stats.total_employers },
            { label: 'Candidates', value: stats.total_candidates },
            { label: 'Open Jobs', value: stats.open_jobs },
          ].map((s) => (
            <div key={s.label} className="bg-white p-4 rounded-xl shadow-sm border border-gray-200 text-center">
              <div className="text-2xl font-bold text-blue-600">{s.value}</div>
              <div className="text-gray-500 text-sm">{s.label}</div>
            </div>
          ))}
        </div>
      )}
      <h2 className="text-xl font-semibold mb-4">Users</h2>
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-50">
            <tr><th className="text-left p-4">Email</th><th className="text-left p-4">Role</th><th className="text-left p-4">Status</th><th className="text-left p-4">Action</th></tr>
          </thead>
          <tbody>
            {users.map((u) => (
              <tr key={u.id} className="border-t border-gray-100">
                <td className="p-4">{u.email}</td>
                <td className="p-4 capitalize">{u.role}</td>
                <td className="p-4"><span className={`px-2 py-1 rounded text-xs font-medium ${u.is_active ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>{u.is_active ? 'Active' : 'Disabled'}</span></td>
                <td className="p-4"><button onClick={() => toggleUser(u.id)} className="text-sm text-blue-600 hover:underline">{u.is_active ? 'Disable' : 'Enable'}</button></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

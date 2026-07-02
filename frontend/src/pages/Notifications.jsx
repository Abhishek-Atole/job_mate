import { useState, useEffect } from 'react'
import api from '../api/client'

export default function Notifications() {
  const [notifications, setNotifications] = useState([])

  useEffect(() => {
    api.get('/notifications/').then((res) => setNotifications(res.data.results || res.data)).catch(console.error)
  }, [])

  const markRead = async (id) => {
    await api.put(`/notifications/${id}/read/`)
    setNotifications(notifications.map((n) => n.id === id ? { ...n, is_read: true } : n))
  }

  return (
    <div className="max-w-3xl mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">Notifications</h1>
      {notifications.length === 0 ? (
        <div className="text-center py-12 text-gray-500">No notifications</div>
      ) : (
        <div className="space-y-3">
          {notifications.map((n) => (
            <div key={n.id} className={`bg-white p-4 rounded-xl shadow-sm border cursor-pointer ${n.is_read ? 'border-gray-200' : 'border-blue-200 bg-blue-50'}`} onClick={() => !n.is_read && markRead(n.id)}>
              <p className={n.is_read ? 'text-gray-600' : 'font-medium'}>{n.message}</p>
              <p className="text-xs text-gray-400 mt-1">{new Date(n.created_at).toLocaleDateString()}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

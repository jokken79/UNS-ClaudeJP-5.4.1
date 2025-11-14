'use client'

import { useState, useEffect } from 'react'

interface Request {
  id: number
  request_type: string
  status: string
  created_by: number
  candidate_id?: string
  employee_id?: number
  created_at: string
  notes?: string
}

export default function RequestsPage() {
  const [requests, setRequests] = useState<Request[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [typeFilter, setTypeFilter] = useState('')
  const [statusFilter, setStatusFilter] = useState('')

  useEffect(() => {
    fetchRequests()
  }, [])

  const fetchRequests = async () => {
    try {
      const token = localStorage.getItem('access_token')
      const response = await fetch('http://localhost:8000/api/requests', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })

      if (!response.ok) throw new Error('Failed to fetch requests')

      const data = await response.json()
      setRequests(data.requests || [])
    } catch (err: any) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const filteredRequests = requests.filter(request => {
    const matchesType = !typeFilter || request.request_type === typeFilter
    const matchesStatus = !statusFilter || request.status === statusFilter
    return matchesType && matchesStatus
  })

  const getRequestTypeLabel = (type: string) => {
    const labels: { [key: string]: string } = {
      'NYUSHA': '入社連絡票',
      'YUKYU': '有給申請',
      'TAISHA': '退社申請',
      'TRANSFER': '配置転換'
    }
    return labels[type] || type
  }

  if (loading) {
    return <div className="flex items-center justify-center min-h-screen"><div className="text-xl text-gray-600 dark:text-gray-400">Loading...</div></div>
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-8">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">
            📋 Request Workflow (申請管理)
          </h1>
          <p className="text-gray-600 dark:text-gray-400">Manage approval workflows for hiring, leave, and transfers</p>
        </div>

        {error && <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg"><p className="text-red-600 dark:text-red-400">{error}</p></div>}

        {/* Filters */}
        <div className="mb-6 bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Request Type
              </label>
              <select
                value={typeFilter}
                onChange={(e) => setTypeFilter(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
              >
                <option value="">All Types</option>
                <option value="NYUSHA">入社連絡票 (New Hire)</option>
                <option value="YUKYU">有給申請 (Paid Leave)</option>
                <option value="TAISHA">退社申請 (Resignation)</option>
                <option value="TRANSFER">配置転換 (Transfer)</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Status
              </label>
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
              >
                <option value="">All Statuses</option>
                <option value="DRAFT">Draft (下書き)</option>
                <option value="PENDING">Pending (承認待ち)</option>
                <option value="APPROVED">Approved (承認済み)</option>
                <option value="REJECTED">Rejected (却下)</option>
              </select>
            </div>

            <div className="flex items-end">
              <button
                onClick={fetchRequests}
                className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
              >
                🔄 Refresh
              </button>
            </div>
          </div>
        </div>

        {/* Summary Cards */}
        <div className="mb-6 grid grid-cols-2 md:grid-cols-4 gap-4">
          {['DRAFT', 'PENDING', 'APPROVED', 'REJECTED'].map(status => {
            const count = requests.filter(r => r.status === status).length
            const colors = {
              'DRAFT': 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300',
              'PENDING': 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
              'APPROVED': 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
              'REJECTED': 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
            }

            return (
              <div key={status} className={`p-4 rounded-lg ${colors[status as keyof typeof colors]}`}>
                <p className="text-sm font-medium">{status}</p>
                <p className="text-2xl font-bold">{count}</p>
              </div>
            )
          })}
        </div>

        {/* Requests Table */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead className="bg-gray-50 dark:bg-gray-900">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">ID</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Type</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Status</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Employee/Candidate</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Created</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
              {filteredRequests.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-6 py-4 text-center text-gray-500 dark:text-gray-400">
                    No requests found
                  </td>
                </tr>
              ) : (
                filteredRequests.map((request) => (
                  <tr key={request.id} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">
                      #{request.id}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                      {getRequestTypeLabel(request.request_type)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 text-xs font-semibold rounded-full
                        ${request.status === 'APPROVED' ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' :
                        request.status === 'PENDING' ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200' :
                        request.status === 'REJECTED' ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200' :
                        'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300'}`}
                      >
                        {request.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                      {request.employee_id || request.candidate_id || '-'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                      {new Date(request.created_at).toLocaleDateString('ja-JP')}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      {request.status === 'PENDING' && (
                        <div className="flex gap-2">
                          <button className="text-green-600 hover:text-green-700 dark:text-green-400">
                            ✓
                          </button>
                          <button className="text-red-600 hover:text-red-700 dark:text-red-400">
                            ✗
                          </button>
                        </div>
                      )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

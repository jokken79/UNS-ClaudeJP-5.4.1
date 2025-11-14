'use client'

import { useState } from 'react'

export default function YukyuPage() {
  const [employeeId, setEmployeeId] = useState('')
  const [balances, setBalances] = useState<any[]>([])
  const [summary, setSummary] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const fetchYukyuData = async () => {
    if (!employeeId) {
      setError('Please enter an employee ID')
      return
    }

    setLoading(true)
    setError('')

    try {
      const token = localStorage.getItem('access_token')

      const [balanceRes, summaryRes] = await Promise.all([
        fetch(`http://localhost:8000/api/yukyu/balance/${employeeId}`, {
          headers: { 'Authorization': `Bearer ${token}` }
        }),
        fetch(`http://localhost:8000/api/yukyu/summary/${employeeId}`, {
          headers: { 'Authorization': `Bearer ${token}` }
        })
      ])

      if (!balanceRes.ok || !summaryRes.ok) throw new Error('Failed to fetch yukyu data')

      const balanceData = await balanceRes.json()
      const summaryData = await summaryRes.json()

      setBalances(balanceData)
      setSummary(summaryData)
    } catch (err: any) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-8">
      <div className="max-w-6xl mx-auto">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">
            🏖️ Yukyu Management (有給休暇)
          </h1>
          <p className="text-gray-600 dark:text-gray-400">Manage paid vacation with LIFO deduction</p>
        </div>

        {/* Search */}
        <div className="mb-6 bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <div className="flex gap-4">
            <input
              type="number"
              placeholder="Enter Employee ID..."
              value={employeeId}
              onChange={(e) => setEmployeeId(e.target.value)}
              className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
            />
            <button
              onClick={fetchYukyuData}
              disabled={loading}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition disabled:opacity-50"
            >
              {loading ? 'Loading...' : 'Search'}
            </button>
          </div>
        </div>

        {error && <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg"><p className="text-red-600 dark:text-red-400">{error}</p></div>}

        {/* Summary */}
        {summary && (
          <div className="mb-6 bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">{summary.employee_name}</h2>

            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                <p className="text-sm text-gray-600 dark:text-gray-400">Total Granted</p>
                <p className="text-2xl font-bold text-blue-600 dark:text-blue-400">{summary.total_granted} days</p>
              </div>

              <div className="p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
                <p className="text-sm text-gray-600 dark:text-gray-400">Total Used</p>
                <p className="text-2xl font-bold text-green-600 dark:text-green-400">{summary.total_used} days</p>
              </div>

              <div className="p-4 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg">
                <p className="text-sm text-gray-600 dark:text-gray-400">Remaining</p>
                <p className="text-2xl font-bold text-yellow-600 dark:text-yellow-400">{summary.total_remaining} days</p>
              </div>

              <div className="p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
                <p className="text-sm text-gray-600 dark:text-gray-400">Usage Rate</p>
                <p className="text-2xl font-bold text-purple-600 dark:text-purple-400">
                  {summary.total_granted > 0 ? Math.round((summary.total_used / summary.total_granted) * 100) : 0}%
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Balances by Fiscal Year */}
        {balances.length > 0 && (
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
              <thead className="bg-gray-50 dark:bg-gray-900">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Fiscal Year</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Granted</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Used</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Remaining</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Grant Date</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Expiry Date</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Status</th>
                </tr>
              </thead>
              <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                {balances.map((balance) => (
                  <tr key={balance.id} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">
                      FY {balance.fiscal_year}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">{balance.granted_days}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">{balance.used_days}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-semibold text-green-600 dark:text-green-400">
                      {balance.remaining_days}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                      {new Date(balance.grant_date).toLocaleDateString('ja-JP')}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                      {new Date(balance.expiry_date).toLocaleDateString('ja-JP')}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 text-xs font-semibold rounded-full ${
                        balance.is_expired
                          ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
                          : 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                      }`}>
                        {balance.is_expired ? 'Expired' : 'Active'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {!summary && !loading && (
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-12 text-center">
            <p className="text-gray-500 dark:text-gray-400">Enter an employee ID to view yukyu balance</p>
          </div>
        )}
      </div>
    </div>
  )
}

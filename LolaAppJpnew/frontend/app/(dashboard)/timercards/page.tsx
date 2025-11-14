'use client'

import { useState } from 'react'

interface TimerCard {
  id: number
  employee_id: number
  work_date: string
  clock_in?: string
  clock_out?: string
  regular_hours: number
  overtime_hours: number
  night_hours: number
  holiday_hours: number
}

export default function TimerCardsPage() {
  const [employeeId, setEmployeeId] = useState('')
  const [year, setYear] = useState(new Date().getFullYear())
  const [month, setMonth] = useState(new Date().getMonth() + 1)
  const [timercards, setTimercards] = useState<TimerCard[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const fetchTimercards = async () => {
    if (!employeeId) {
      setError('Please enter an employee ID')
      return
    }

    setLoading(true)
    setError('')

    try {
      const token = localStorage.getItem('access_token')
      const response = await fetch(
        `http://localhost:8000/api/timercards/employee/${employeeId}?year=${year}&month=${month}`,
        {
          headers: { 'Authorization': `Bearer ${token}` }
        }
      )

      if (!response.ok) throw new Error('Failed to fetch timercards')

      const data = await response.json()
      setTimercards(data.timercards || [])
    } catch (err: any) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const totalHours = timercards.reduce((acc, tc) => ({
    regular: acc.regular + tc.regular_hours,
    overtime: acc.overtime + tc.overtime_hours,
    night: acc.night + tc.night_hours,
    holiday: acc.holiday + tc.holiday_hours,
  }), { regular: 0, overtime: 0, night: 0, holiday: 0 })

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-8">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">
            ⏰ Timer Cards (タイムカード)
          </h1>
          <p className="text-gray-600 dark:text-gray-400">Track daily attendance and hours</p>
        </div>

        {/* Search Filters */}
        <div className="mb-6 bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <input
              type="number"
              placeholder="Employee ID"
              value={employeeId}
              onChange={(e) => setEmployeeId(e.target.value)}
              className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
            />

            <select
              value={year}
              onChange={(e) => setYear(parseInt(e.target.value))}
              className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
            >
              {[2023, 2024, 2025, 2026].map(y => (
                <option key={y} value={y}>{y}</option>
              ))}
            </select>

            <select
              value={month}
              onChange={(e) => setMonth(parseInt(e.target.value))}
              className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
            >
              {[1,2,3,4,5,6,7,8,9,10,11,12].map(m => (
                <option key={m} value={m}>{m}月</option>
              ))}
            </select>

            <button
              onClick={fetchTimercards}
              disabled={loading}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition disabled:opacity-50"
            >
              {loading ? 'Loading...' : 'Search'}
            </button>
          </div>
        </div>

        {error && <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg"><p className="text-red-600 dark:text-red-400">{error}</p></div>}

        {/* Summary */}
        {timercards.length > 0 && (
          <div className="mb-6 grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
              <p className="text-sm text-gray-600 dark:text-gray-400">Regular Hours</p>
              <p className="text-2xl font-bold text-blue-600 dark:text-blue-400">{totalHours.regular.toFixed(1)}h</p>
            </div>
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
              <p className="text-sm text-gray-600 dark:text-gray-400">Overtime Hours</p>
              <p className="text-2xl font-bold text-orange-600 dark:text-orange-400">{totalHours.overtime.toFixed(1)}h</p>
            </div>
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
              <p className="text-sm text-gray-600 dark:text-gray-400">Night Hours</p>
              <p className="text-2xl font-bold text-purple-600 dark:text-purple-400">{totalHours.night.toFixed(1)}h</p>
            </div>
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
              <p className="text-sm text-gray-600 dark:text-gray-400">Holiday Hours</p>
              <p className="text-2xl font-bold text-green-600 dark:text-green-400">{totalHours.holiday.toFixed(1)}h</p>
            </div>
          </div>
        )}

        {/* Timercards Table */}
        {timercards.length > 0 && (
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
              <thead className="bg-gray-50 dark:bg-gray-900">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Date</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Clock In</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Clock Out</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Regular</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">OT</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Night</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Holiday</th>
                </tr>
              </thead>
              <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                {timercards.map((tc) => (
                  <tr key={tc.id} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">
                      {new Date(tc.work_date).toLocaleDateString('ja-JP')}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                      {tc.clock_in ? new Date(tc.clock_in).toLocaleTimeString('ja-JP', { hour: '2-digit', minute: '2-digit' }) : '-'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                      {tc.clock_out ? new Date(tc.clock_out).toLocaleTimeString('ja-JP', { hour: '2-digit', minute: '2-digit' }) : '-'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">{tc.regular_hours}h</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-orange-600 dark:text-orange-400">{tc.overtime_hours}h</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-purple-600 dark:text-purple-400">{tc.night_hours}h</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-green-600 dark:text-green-400">{tc.holiday_hours}h</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {!loading && timercards.length === 0 && employeeId && (
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-12 text-center">
            <p className="text-gray-500 dark:text-gray-400">No timercards found for this period</p>
          </div>
        )}

        {!employeeId && !loading && (
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-12 text-center">
            <p className="text-gray-500 dark:text-gray-400">Enter an employee ID to view timercards</p>
          </div>
        )}
      </div>
    </div>
  )
}

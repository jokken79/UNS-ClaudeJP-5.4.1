'use client'

import { useState } from 'react'

interface PayrollResult {
  employee_id: number
  employee_name: string
  year: number
  month: number
  gross_pay: number
  net_pay: number
  total_regular_hours: number
  total_overtime_hours: number
  total_deductions: number
  hourly_rate: number
}

export default function PayrollPage() {
  const [employeeId, setEmployeeId] = useState('')
  const [year, setYear] = useState(new Date().getFullYear())
  const [month, setMonth] = useState(new Date().getMonth() + 1)
  const [payroll, setPayroll] = useState<PayrollResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const calculatePayroll = async () => {
    if (!employeeId) {
      setError('Please enter an employee ID')
      return
    }

    setLoading(true)
    setError('')

    try {
      const token = localStorage.getItem('access_token')
      const response = await fetch('http://localhost:8000/api/payroll/calculate', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          employee_id: parseInt(employeeId),
          year,
          month
        })
      })

      if (!response.ok) throw new Error('Failed to calculate payroll')

      const data = await response.json()
      setPayroll(data)
    } catch (err: any) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-8">
      <div className="max-w-5xl mx-auto">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">
            💰 Payroll Calculations (給与)
          </h1>
          <p className="text-gray-600 dark:text-gray-400">Calculate monthly payroll with deductions</p>
        </div>

        {/* Calculation Form */}
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
              onClick={calculatePayroll}
              disabled={loading}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition disabled:opacity-50"
            >
              {loading ? 'Calculating...' : 'Calculate'}
            </button>
          </div>
        </div>

        {error && <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg"><p className="text-red-600 dark:text-red-400">{error}</p></div>}

        {/* Payroll Results */}
        {payroll && (
          <div className="space-y-6">
            {/* Employee Info */}
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
                {payroll.employee_name}
              </h2>
              <p className="text-gray-600 dark:text-gray-400">
                Employee ID: {payroll.employee_id} | Period: {payroll.year}年{payroll.month}月
              </p>
            </div>

            {/* Hours Breakdown */}
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Hours Worked</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Regular Hours</p>
                  <p className="text-xl font-bold text-gray-900 dark:text-white">{payroll.total_regular_hours}h</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Overtime Hours</p>
                  <p className="text-xl font-bold text-orange-600 dark:text-orange-400">{payroll.total_overtime_hours}h</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Hourly Rate</p>
                  <p className="text-xl font-bold text-gray-900 dark:text-white">¥{payroll.hourly_rate.toLocaleString()}</p>
                </div>
              </div>
            </div>

            {/* Pay Breakdown */}
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Pay Breakdown</h3>

              <div className="space-y-3">
                <div className="flex justify-between items-center p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
                  <span className="font-medium text-gray-900 dark:text-white">Gross Pay (総支給額)</span>
                  <span className="text-xl font-bold text-green-600 dark:text-green-400">
                    ¥{payroll.gross_pay.toLocaleString()}
                  </span>
                </div>

                <div className="flex justify-between items-center p-3 bg-red-50 dark:bg-red-900/20 rounded-lg">
                  <span className="font-medium text-gray-900 dark:text-white">Total Deductions (控除)</span>
                  <span className="text-xl font-bold text-red-600 dark:text-red-400">
                    -¥{payroll.total_deductions.toLocaleString()}
                  </span>
                </div>

                <div className="flex justify-between items-center p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border-2 border-blue-500">
                  <span className="text-lg font-bold text-gray-900 dark:text-white">Net Pay (手取り)</span>
                  <span className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                    ¥{payroll.net_pay.toLocaleString()}
                  </span>
                </div>
              </div>
            </div>
          </div>
        )}

        {!payroll && !loading && (
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-12 text-center">
            <p className="text-gray-500 dark:text-gray-400">Enter an employee ID and select a period to calculate payroll</p>
          </div>
        )}
      </div>
    </div>
  )
}

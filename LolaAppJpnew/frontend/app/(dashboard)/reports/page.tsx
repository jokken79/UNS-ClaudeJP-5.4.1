'use client'

import { useState } from 'react'

export default function ReportsPage() {
  const [selectedReport, setSelectedReport] = useState('')
  const [year, setYear] = useState(new Date().getFullYear())
  const [month, setMonth] = useState(new Date().getMonth() + 1)

  const reports = [
    {
      id: 'employee-summary',
      name: 'Employee Summary Report',
      description: 'Overview of all active employees',
      icon: '👥'
    },
    {
      id: 'payroll-summary',
      name: 'Payroll Summary Report',
      description: 'Monthly payroll calculations',
      icon: '💰'
    },
    {
      id: 'attendance-summary',
      name: 'Attendance Summary',
      description: 'Monthly attendance tracking',
      icon: '⏰'
    },
    {
      id: 'yukyu-summary',
      name: 'Yukyu Balance Report',
      description: 'Paid vacation balance for all employees',
      icon: '🏖️'
    },
    {
      id: 'apartment-occupancy',
      name: 'Apartment Occupancy',
      description: 'Current apartment utilization',
      icon: '🏠'
    },
    {
      id: 'request-workflow',
      name: 'Request Workflow Status',
      description: 'Pending approvals and workflow status',
      icon: '📋'
    }
  ]

  const handleGenerateReport = () => {
    if (!selectedReport) {
      alert('Please select a report type')
      return
    }

    alert(`Generating ${selectedReport} for ${year}年${month}月...\n\nThis feature will export to PDF/Excel.`)
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-8">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">
            📊 Reports (レポート)
          </h1>
          <p className="text-gray-600 dark:text-gray-400">Generate comprehensive reports for HR management</p>
        </div>

        {/* Report Selection */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          {reports.map((report) => (
            <div
              key={report.id}
              onClick={() => setSelectedReport(report.id)}
              className={`p-6 rounded-lg cursor-pointer transition ${
                selectedReport === report.id
                  ? 'bg-blue-50 dark:bg-blue-900/20 border-2 border-blue-500 shadow-lg'
                  : 'bg-white dark:bg-gray-800 border-2 border-gray-200 dark:border-gray-700 hover:border-blue-300 dark:hover:border-blue-700 shadow'
              }`}
            >
              <div className="text-4xl mb-3">{report.icon}</div>
              <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-2">
                {report.name}
              </h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                {report.description}
              </p>
            </div>
          ))}
        </div>

        {/* Report Options */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 mb-6">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
            Report Options
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Year
              </label>
              <select
                value={year}
                onChange={(e) => setYear(parseInt(e.target.value))}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
              >
                {[2023, 2024, 2025, 2026].map(y => (
                  <option key={y} value={y}>{y}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Month
              </label>
              <select
                value={month}
                onChange={(e) => setMonth(parseInt(e.target.value))}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
              >
                {[1,2,3,4,5,6,7,8,9,10,11,12].map(m => (
                  <option key={m} value={m}>{m}月</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Format
              </label>
              <select
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
              >
                <option value="pdf">PDF</option>
                <option value="excel">Excel</option>
                <option value="csv">CSV</option>
              </select>
            </div>
          </div>

          <div className="flex gap-4">
            <button
              onClick={handleGenerateReport}
              disabled={!selectedReport}
              className="flex-1 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed font-semibold"
            >
              📥 Generate Report
            </button>

            <button
              onClick={() => alert('Preview functionality coming soon!')}
              disabled={!selectedReport}
              className="px-6 py-3 bg-gray-200 dark:bg-gray-700 text-gray-900 dark:text-white rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition disabled:opacity-50 disabled:cursor-not-allowed font-semibold"
            >
              👁️ Preview
            </button>
          </div>
        </div>

        {/* Report Information */}
        <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-blue-900 dark:text-blue-200 mb-3">
            ℹ️ Report Information
          </h3>
          <ul className="space-y-2 text-sm text-blue-800 dark:text-blue-300">
            <li>• Reports are generated in real-time based on the selected period</li>
            <li>• PDF format is recommended for printing and archival</li>
            <li>• Excel format allows for further data analysis</li>
            <li>• All reports include metadata (generation date, user, etc.)</li>
            <li>• Historical data is preserved according to Japanese labor law requirements</li>
          </ul>
        </div>

        {!selectedReport && (
          <div className="mt-6 bg-white dark:bg-gray-800 rounded-lg shadow p-12 text-center">
            <p className="text-gray-500 dark:text-gray-400 text-lg">
              ↑ Select a report type to continue
            </p>
          </div>
        )}
      </div>
    </div>
  )
}

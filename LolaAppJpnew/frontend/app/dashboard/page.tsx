export default function DashboardPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
      <div className="container mx-auto px-4 py-16">
        <div className="text-center">
          <h1 className="text-6xl font-bold text-gray-900 dark:text-white mb-4">
            🚀 LolaAppJp
          </h1>
          <p className="text-2xl text-gray-700 dark:text-gray-300 mb-8">
            HR Management System for Japanese Staffing Agencies
          </p>

          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl p-8 max-w-3xl mx-auto">
            <h2 className="text-3xl font-semibold mb-6 text-gray-800 dark:text-white">
              ✅ Application is Running!
            </h2>

            <div className="space-y-4 text-left">
              <div className="p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
                <h3 className="font-bold text-lg mb-2 text-green-800 dark:text-green-300">
                  🎯 Core Features
                </h3>
                <ul className="list-disc list-inside space-y-1 text-gray-700 dark:text-gray-300">
                  <li>Candidate Management (履歴書/Rirekisho)</li>
                  <li>入社連絡票 Workflow (New Hire Notification)</li>
                  <li>Employee Management with Factory Assignment</li>
                  <li>Intelligent Apartment Management</li>
                  <li>Yukyu (有給休暇) with LIFO deduction</li>
                  <li>Timer Cards OCR Processing</li>
                  <li>Payroll Calculations</li>
                </ul>
              </div>

              <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                <h3 className="font-bold text-lg mb-2 text-blue-800 dark:text-blue-300">
                  🔗 Quick Links
                </h3>
                <ul className="space-y-2 text-gray-700 dark:text-gray-300">
                  <li>
                    <a
                      href="/api/docs"
                      className="text-blue-600 dark:text-blue-400 hover:underline"
                    >
                      📚 API Documentation (Swagger)
                    </a>
                  </li>
                  <li>
                    <a
                      href="http://localhost:8080"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-600 dark:text-blue-400 hover:underline"
                    >
                      🗄️ Database UI (Adminer)
                    </a>
                  </li>
                  <li>
                    <a
                      href="http://localhost:3001"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-600 dark:text-blue-400 hover:underline"
                    >
                      📊 Grafana Dashboards
                    </a>
                  </li>
                  <li>
                    <a
                      href="http://localhost:9090"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-600 dark:text-blue-400 hover:underline"
                    >
                      📈 Prometheus Metrics
                    </a>
                  </li>
                </ul>
              </div>

              <div className="p-4 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg">
                <h3 className="font-bold text-lg mb-2 text-yellow-800 dark:text-yellow-300">
                  🔐 Default Login
                </h3>
                <p className="text-gray-700 dark:text-gray-300">
                  <strong>Username:</strong> admin<br />
                  <strong>Password:</strong> admin123<br />
                  <span className="text-sm text-red-600 dark:text-red-400">
                    ⚠️ Change this password after first login!
                  </span>
                </p>
              </div>

              <div className="p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
                <h3 className="font-bold text-lg mb-2 text-purple-800 dark:text-purple-300">
                  📖 Next Steps
                </h3>
                <ol className="list-decimal list-inside space-y-1 text-gray-700 dark:text-gray-300">
                  <li>Review the README.md for complete documentation</li>
                  <li>Configure .env file with your settings</li>
                  <li>Access API docs to explore available endpoints</li>
                  <li>Start implementing your custom pages</li>
                </ol>
              </div>
            </div>

            <div className="mt-8 p-4 bg-gray-100 dark:bg-gray-700 rounded-lg">
              <p className="text-sm text-gray-600 dark:text-gray-400 text-center">
                Built with FastAPI 0.115.6, Next.js 16.0.0, React 19.0.0, TypeScript 5.6<br />
                PostgreSQL 15, Redis 7, Docker Compose<br />
                OpenTelemetry + Prometheus + Grafana for Observability
              </p>
            </div>
          </div>

          <div className="mt-8 text-gray-600 dark:text-gray-400">
            <p className="text-sm">
              Made with ❤️ for Japanese HR professionals
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

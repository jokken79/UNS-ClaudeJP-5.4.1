'use client'

import { useState, useEffect } from 'react'

interface Plant {
  id: number
  company_id: number
  name: string
  address?: string
  latitude?: number
  longitude?: number
}

interface Line {
  id: number
  plant_id: number
  line_number?: string
  name: string
  hourly_rate: number
}

export default function FactoriesPage() {
  const [plants, setPlants] = useState<Plant[]>([])
  const [lines, setLines] = useState<Line[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [selectedPlant, setSelectedPlant] = useState<number | null>(null)

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      const token = localStorage.getItem('access_token')

      const [plantsRes, linesRes] = await Promise.all([
        fetch('http://localhost:8000/api/plants', { headers: { 'Authorization': `Bearer ${token}` } }),
        fetch('http://localhost:8000/api/lines', { headers: { 'Authorization': `Bearer ${token}` } })
      ])

      if (!plantsRes.ok || !linesRes.ok) throw new Error('Failed to fetch data')

      const plantsData = await plantsRes.json()
      const linesData = await linesRes.json()

      setPlants(plantsData.plants || [])
      setLines(linesData.lines || [])
    } catch (err: any) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const filteredLines = selectedPlant ? lines.filter(line => line.plant_id === selectedPlant) : []

  if (loading) {
    return <div className="flex items-center justify-center min-h-screen"><div className="text-xl text-gray-600 dark:text-gray-400">Loading...</div></div>
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-8">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">
            🏭 Factory Management
          </h1>
          <p className="text-gray-600 dark:text-gray-400">Manage plants (工場) and production lines (生産ライン)</p>
        </div>

        {error && <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg"><p className="text-red-600 dark:text-red-400">{error}</p></div>}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Plants List */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">Plants (工場)</h2>

            <div className="space-y-2">
              {plants.map((plant) => (
                <div
                  key={plant.id}
                  onClick={() => setSelectedPlant(plant.id)}
                  className={`p-4 rounded-lg cursor-pointer transition ${
                    selectedPlant === plant.id
                      ? 'bg-blue-50 dark:bg-blue-900/20 border-2 border-blue-500'
                      : 'bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-600'
                  }`}
                >
                  <h3 className="font-semibold text-gray-900 dark:text-white">{plant.name}</h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400">{plant.address || 'No address'}</p>
                  <p className="text-xs text-gray-500 dark:text-gray-500 mt-1">
                    {lines.filter(l => l.plant_id === plant.id).length} production lines
                  </p>
                </div>
              ))}

              {plants.length === 0 && (
                <p className="text-gray-500 dark:text-gray-400 text-center py-8">No plants found</p>
              )}
            </div>
          </div>

          {/* Production Lines */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">Production Lines (生産ライン)</h2>

            {selectedPlant ? (
              <div className="space-y-2">
                {filteredLines.map((line) => (
                  <div key={line.id} className="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                    <div className="flex justify-between items-start">
                      <div>
                        <h3 className="font-semibold text-gray-900 dark:text-white">{line.name}</h3>
                        {line.line_number && (
                          <p className="text-sm text-gray-600 dark:text-gray-400">{line.line_number}</p>
                        )}
                      </div>
                      <div className="text-right">
                        <p className="text-sm font-semibold text-green-600 dark:text-green-400">
                          ¥{line.hourly_rate.toLocaleString()}/hr
                        </p>
                      </div>
                    </div>
                  </div>
                ))}

                {filteredLines.length === 0 && (
                  <p className="text-gray-500 dark:text-gray-400 text-center py-8">No production lines for this plant</p>
                )}
              </div>
            ) : (
              <p className="text-gray-500 dark:text-gray-400 text-center py-8">Select a plant to view production lines</p>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

'use client'

import { useState, useEffect } from 'react'

interface Apartment {
  id: number
  name: string
  address?: string
  total_capacity: number
  current_occupancy: number
  monthly_rent?: number
  latitude?: number
  longitude?: number
}

export default function ApartmentsPage() {
  const [apartments, setApartments] = useState<Apartment[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    fetchApartments()
  }, [])

  const fetchApartments = async () => {
    try {
      const token = localStorage.getItem('access_token')
      const response = await fetch('http://localhost:8000/api/apartments', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })

      if (!response.ok) throw new Error('Failed to fetch apartments')

      const data = await response.json()
      setApartments(data.apartments || [])
    } catch (err: any) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="flex items-center justify-center min-h-screen"><div className="text-xl text-gray-600 dark:text-gray-400">Loading...</div></div>
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-8">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">
            🏠 Apartment Management
          </h1>
          <p className="text-gray-600 dark:text-gray-400">Manage employee housing (社員寮)</p>
        </div>

        {error && <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg"><p className="text-red-600 dark:text-red-400">{error}</p></div>}

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {apartments.map((apartment) => (
            <div key={apartment.id} className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
              <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2">{apartment.name}</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">{apartment.address || 'No address'}</p>

              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">Capacity:</span>
                  <span className="font-semibold text-gray-900 dark:text-white">{apartment.current_occupancy} / {apartment.total_capacity}</span>
                </div>

                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full ${
                      (apartment.current_occupancy / apartment.total_capacity) >= 0.9 ? 'bg-red-500' :
                      (apartment.current_occupancy / apartment.total_capacity) >= 0.7 ? 'bg-yellow-500' : 'bg-green-500'
                    }`}
                    style={{ width: `${(apartment.current_occupancy / apartment.total_capacity) * 100}%` }}
                  />
                </div>

                {apartment.monthly_rent && (
                  <div className="flex justify-between pt-2 border-t border-gray-200 dark:border-gray-700">
                    <span className="text-gray-600 dark:text-gray-400">Rent:</span>
                    <span className="font-semibold text-gray-900 dark:text-white">¥{apartment.monthly_rent.toLocaleString()}</span>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>

        {apartments.length === 0 && (
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-12 text-center">
            <p className="text-gray-500 dark:text-gray-400">No apartments found</p>
          </div>
        )}
      </div>
    </div>
  )
}

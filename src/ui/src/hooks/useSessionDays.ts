import { useState, useEffect } from 'react'
import { sessionDayApi } from '@/services/sessionDayApi'
import type { 
  CourseSessionDay, 
  CreateCourseSessionDayRequest, 
  UpdateCourseSessionDayRequest 
} from '@/types/courseSession'

export const useSessionDays = (filters?: {
  start_date?: string
  end_date?: string
  location_id?: number
  skip?: number
  limit?: number
}) => {
  const [sessionDays, setSessionDays] = useState<CourseSessionDay[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchSessionDays = async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await sessionDayApi.list(filters)
      setSessionDays(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch session days')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchSessionDays()
  }, [JSON.stringify(filters)])

  const createSessionDay = async (sessionId: number, sessionDay: CreateCourseSessionDayRequest) => {
    try {
      const newSessionDay = await sessionDayApi.create(sessionId, sessionDay)
      setSessionDays(prev => [...prev, newSessionDay])
      return newSessionDay
    } catch (err) {
      throw new Error(err instanceof Error ? err.message : 'Failed to create session day')
    }
  }

  const updateSessionDay = async (sessionDayId: number, sessionDay: UpdateCourseSessionDayRequest) => {
    try {
      const updatedSessionDay = await sessionDayApi.update(sessionDayId, sessionDay)
      setSessionDays(prev => 
        prev.map(sd => sd.id === sessionDayId ? updatedSessionDay : sd)
      )
      return updatedSessionDay
    } catch (err) {
      throw new Error(err instanceof Error ? err.message : 'Failed to update session day')
    }
  }

  const deleteSessionDay = async (sessionDayId: number) => {
    try {
      await sessionDayApi.delete(sessionDayId)
      setSessionDays(prev => prev.filter(sd => sd.id !== sessionDayId))
    } catch (err) {
      throw new Error(err instanceof Error ? err.message : 'Failed to delete session day')
    }
  }

  return {
    sessionDays,
    loading,
    error,
    refetch: fetchSessionDays,
    createSessionDay,
    updateSessionDay,
    deleteSessionDay
  }
}

export const useSessionDaysBySession = (sessionId: number) => {
  const [sessionDays, setSessionDays] = useState<CourseSessionDay[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchSessionDays = async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await sessionDayApi.getBySessionId(sessionId)
      setSessionDays(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch session days')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (sessionId) {
      fetchSessionDays()
    }
  }, [sessionId])

  const createSessionDay = async (sessionDay: CreateCourseSessionDayRequest) => {
    try {
      const newSessionDay = await sessionDayApi.create(sessionId, sessionDay)
      setSessionDays(prev => [...prev, newSessionDay].sort((a, b) => a.day_number - b.day_number))
      return newSessionDay
    } catch (err) {
      throw new Error(err instanceof Error ? err.message : 'Failed to create session day')
    }
  }

  const updateSessionDay = async (sessionDayId: number, sessionDay: UpdateCourseSessionDayRequest) => {
    try {
      const updatedSessionDay = await sessionDayApi.update(sessionDayId, sessionDay)
      setSessionDays(prev => 
        prev.map(sd => sd.id === sessionDayId ? updatedSessionDay : sd)
          .sort((a, b) => a.day_number - b.day_number)
      )
      return updatedSessionDay
    } catch (err) {
      throw new Error(err instanceof Error ? err.message : 'Failed to update session day')
    }
  }

  const deleteSessionDay = async (sessionDayId: number) => {
    try {
      await sessionDayApi.delete(sessionDayId)
      setSessionDays(prev => prev.filter(sd => sd.id !== sessionDayId))
    } catch (err) {
      throw new Error(err instanceof Error ? err.message : 'Failed to delete session day')
    }
  }

  return {
    sessionDays,
    loading,
    error,
    refetch: fetchSessionDays,
    createSessionDay,
    updateSessionDay,
    deleteSessionDay
  }
}
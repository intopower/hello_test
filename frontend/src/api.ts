import type { CreateTaskMetadata, VideoTask } from './types'

export const API_BASE = import.meta.env.VITE_API_BASE ?? 'http://localhost:8000/api'
export const API_ORIGIN = (() => {
  try {
    const url = new URL(API_BASE)
    return `${url.protocol}//${url.host}`
  } catch {
    return API_BASE.replace(/\/api\/?$/, '')
  }
})()

export async function fetchTasks(): Promise<VideoTask[]> {
  const res = await fetch(`${API_BASE}/tasks`)
  if (!res.ok) {
    throw new Error('获取任务列表失败')
  }
  return res.json()
}

export async function createTask(metadata: CreateTaskMetadata, file?: File | null) {
  const formData = new FormData()
  formData.append('metadata', JSON.stringify(metadata))
  if (file) {
    formData.append('file', file)
  }

  const res = await fetch(`${API_BASE}/tasks`, {
    method: 'POST',
    body: formData,
  })

  if (!res.ok) {
    const detail = await res.json().catch(() => ({}))
    throw new Error(detail?.detail ?? '创建任务失败')
  }

  return res.json()
}

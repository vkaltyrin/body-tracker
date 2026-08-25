/**
 * Клиент API. Пока напрямую из приложения — на этапе с `packages/core`
 * переедет туда вместе с офлайн-очередью и локальным кэшем.
 */

const BASE = 'http://localhost:4318'

export type Entry = {
  day: string
  yoga: boolean
  gym: boolean
  note: string
  updated_at: string
  rev: number
}

export type Today = {
  today: string
  yoga_done: boolean
  gym_done: boolean
  week: { from: string; to: string; yoga: number; gym: number }
  target: { yoga: number; gym: number }
}

export type PlanDay = {
  dow: number
  axis: string
  detail: string
  priority: number | null
  gym: { session: string; optional: boolean } | null
}

export type Plan = {
  version: number
  name: string
  targets: { yoga: number; gym: number }
  priorities: { rank: number; title: string }[]
  days: PlanDay[]
}

async function call<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    ...init,
    headers: { 'Content-Type': 'application/json', ...init?.headers },
  })
  if (!res.ok) {
    const body = (await res.json().catch(() => ({}))) as { detail?: string }
    throw new Error(body.detail ?? `Запрос не прошёл (${res.status})`)
  }
  return (await res.json()) as T
}

export const getPlan = () => call<Plan>('/api/plan')

export const getToday = (day: string) => call<Today>(`/api/today?day=${day}`)

export const getRange = (from: string, to: string) =>
  call<Entry[]>(`/api/entries?from=${from}&to=${to}`)

export const toggleToday = (day: string, field: 'yoga' | 'gym') =>
  call<Entry>(`/api/today/toggle?day=${day}`, {
    method: 'POST',
    body: JSON.stringify({ field }),
  })

export const putEntry = (day: string, patch: Pick<Entry, 'yoga' | 'gym'>) =>
  call<Entry>(`/api/entries/${day}`, {
    method: 'PUT',
    body: JSON.stringify({ ...patch, note: '', updated_at: new Date().toISOString() }),
  })

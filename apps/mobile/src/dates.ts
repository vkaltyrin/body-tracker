export const DOW = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'] as const

const MONTHS_GEN = [
  'января', 'февраля', 'марта', 'апреля', 'мая', 'июня',
  'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря',
] as const

const WEEKDAYS = [
  'Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье',
] as const

/** Локальная дата клиента. Сервер живёт в UTC и своей дате не доверяет. */
export const key = (d: Date): string =>
  `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`

export const addDays = (d: Date, n: number): Date => {
  const c = new Date(d)
  c.setDate(c.getDate() + n)
  return c
}

/** 0 = понедельник */
export const dowIndex = (d: Date): number => (d.getDay() + 6) % 7

export const startOfWeek = (d: Date): Date => addDays(d, -dowIndex(d))

export const isoDow = (d: Date): number => dowIndex(d) + 1

export const longDate = (d: Date): string =>
  `${WEEKDAYS[dowIndex(d)]}, ${d.getDate()} ${MONTHS_GEN[d.getMonth()]}`

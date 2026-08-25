import { StatusBar } from 'expo-status-bar'
import { useCallback, useEffect, useMemo, useState } from 'react'
import {
  ActivityIndicator,
  Pressable,
  RefreshControl,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from 'react-native'
import { SafeAreaProvider, SafeAreaView } from 'react-native-safe-area-context'

import * as api from './src/api'
import { DOW, addDays, isoDow, key, longDate, startOfWeek } from './src/dates'
import { C, MONO } from './src/theme'

type Field = 'yoga' | 'gym'

export default function App() {
  const now = useMemo(() => new Date(), [])
  const today = key(now)
  const monday = useMemo(() => startOfWeek(now), [now])

  const [plan, setPlan] = useState<api.Plan | null>(null)
  const [state, setState] = useState<api.Today | null>(null)
  const [week, setWeek] = useState<Record<string, api.Entry>>({})
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)

  const load = useCallback(async () => {
    try {
      const [p, t, entries] = await Promise.all([
        plan ? Promise.resolve(plan) : api.getPlan(),
        api.getToday(today),
        api.getRange(key(monday), key(addDays(monday, 6))),
      ])
      setPlan(p)
      setState(t)
      setWeek(Object.fromEntries(entries.map((e) => [e.day, e])))
      setError(null)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Не удалось получить данные')
    }
  }, [monday, plan, today])

  useEffect(() => {
    void load()
  }, [load])

  const refresh = useCallback(async () => {
    setBusy(true)
    await load()
    setBusy(false)
  }, [load])

  const toggleToday = async (field: Field) => {
    // Оптимистично: интерфейс не ждёт сеть.
    setState((s) => (s ? { ...s, [`${field}_done`]: !s[`${field}_done`] } : s))
    try {
      await api.toggleToday(today, field)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Отметка не сохранилась')
    }
    void load()
  }

  const toggleDay = async (day: string, field: Field) => {
    const current = week[day] ?? { day, yoga: false, gym: false }
    const next = { yoga: current.yoga, gym: current.gym, [field]: !current[field] }
    setWeek((w) => ({ ...w, [day]: { ...(w[day] as api.Entry), ...next, day } }))
    try {
      await api.putEntry(day, next)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Отметка не сохранилась')
    }
    void load()
  }

  const planDay = plan?.days.find((d) => d.dow === isoDow(now))

  if (!state || !plan) {
    return (
      <SafeAreaProvider>
        <View style={[s.screen, s.center]}>
          <StatusBar style="light" />
          {error ? <Text style={s.error}>{error}</Text> : <ActivityIndicator color={C.muted} />}
        </View>
      </SafeAreaProvider>
    )
  }

  return (
    <SafeAreaProvider>
      <StatusBar style="light" />
      <SafeAreaView style={s.screen} edges={['top', 'bottom']}>
        <ScrollView
          contentContainerStyle={s.content}
          refreshControl={
            <RefreshControl refreshing={busy} onRefresh={refresh} tintColor={C.muted} />
          }
        >
          <Text style={s.eyebrow}>{longDate(now).toUpperCase()}</Text>

          <View style={s.axis}>
            <Text style={s.axisTitle}>{planDay?.axis ?? '—'}</Text>
            {planDay?.detail ? <Text style={s.axisDetail}>{planDay.detail}</Text> : null}
            <View style={s.tags}>
              {planDay?.priority ? (
                <Text style={[s.tag, s.tagPriority]}>Приоритет {planDay.priority}</Text>
              ) : null}
              {planDay?.gym ? (
                <Text style={[s.tag, s.tagGym]}>
                  Вечер · {planDay.gym.session}
                  {planDay.gym.optional ? ' · опц.' : ''}
                </Text>
              ) : (
                <Text style={s.tag}>Зала сегодня нет</Text>
              )}
            </View>
          </View>

          <View style={s.buttons}>
            <Big
              label="Йога"
              letter="Y"
              on={state.yoga_done}
              color={C.yoga}
              soft={C.yogaSoft}
              onPress={() => toggleToday('yoga')}
            />
            <Big
              label="Зал"
              letter="G"
              on={state.gym_done}
              color={C.gym}
              soft={C.gymSoft}
              onPress={() => toggleToday('gym')}
            />
          </View>

          <Text style={s.section}>ЦЕЛЬ НЕДЕЛИ</Text>
          <Progress
            label="Йога"
            value={state.week.yoga}
            target={state.target.yoga}
            color={C.yoga}
          />
          <Progress label="Зал" value={state.week.gym} target={state.target.gym} color={C.gym} />

          <Text style={s.section}>НЕДЕЛЯ</Text>
          <View style={s.strip}>
            {Array.from({ length: 7 }, (_, i) => {
              const d = addDays(monday, i)
              const k = key(d)
              const e = week[k]
              const isToday = k === today
              return (
                <View key={k} style={[s.cell, isToday && s.cellToday]}>
                  <Text style={s.cellDow}>{DOW[i]}</Text>
                  <Text style={[s.cellDate, isToday && s.cellDateToday]}>{d.getDate()}</Text>
                  <Dot on={!!e?.yoga} color={C.yoga} onPress={() => toggleDay(k, 'yoga')} />
                  <Dot on={!!e?.gym} color={C.gym} onPress={() => toggleDay(k, 'gym')} />
                </View>
              )
            })}
          </View>

          {error ? <Text style={s.error}>{error}</Text> : null}
        </ScrollView>
      </SafeAreaView>
    </SafeAreaProvider>
  )
}

function Big({
  label,
  letter,
  on,
  color,
  soft,
  onPress,
}: {
  label: string
  letter: string
  on: boolean
  color: string
  soft: string
  onPress: () => void
}) {
  return (
    <Pressable
      accessibilityRole="button"
      accessibilityState={{ selected: on }}
      onPress={onPress}
      style={({ pressed }) => [
        s.big,
        { backgroundColor: on ? color : soft, borderColor: on ? color : C.line },
        pressed && s.pressed,
      ]}
    >
      <Text style={[s.bigLetter, { color: on ? '#0F1311' : color }]}>{letter}</Text>
      <Text style={[s.bigLabel, { color: on ? '#0F1311' : C.muted }]}>{label}</Text>
    </Pressable>
  )
}

function Progress({
  label,
  value,
  target,
  color,
}: {
  label: string
  value: number
  target: number
  color: string
}) {
  return (
    <View style={s.progress}>
      <Text style={s.progressLabel}>{label}</Text>
      <View style={s.pips}>
        {Array.from({ length: target }, (_, i) => (
          <View
            key={i}
            style={[s.pip, { backgroundColor: i < value ? color : C.line }]}
          />
        ))}
      </View>
      <Text style={s.progressValue}>
        {value} / {target}
      </Text>
    </View>
  )
}

function Dot({ on, color, onPress }: { on: boolean; color: string; onPress: () => void }) {
  return (
    <Pressable
      accessibilityRole="button"
      accessibilityState={{ selected: on }}
      onPress={onPress}
      hitSlop={4}
      style={({ pressed }) => [
        s.dot,
        { backgroundColor: on ? color : 'transparent', borderColor: on ? color : C.line },
        pressed && s.pressed,
      ]}
    />
  )
}

const s = StyleSheet.create({
  screen: { flex: 1, backgroundColor: C.bg },
  center: { alignItems: 'center', justifyContent: 'center' },
  content: { padding: 20, gap: 18 },

  eyebrow: { fontFamily: MONO, fontSize: 11, letterSpacing: 1.4, color: C.faint },

  axis: { gap: 6 },
  axisTitle: { fontSize: 27, fontWeight: '600', color: C.text, letterSpacing: -0.4 },
  axisDetail: { fontSize: 16, color: C.muted },
  tags: { flexDirection: 'row', flexWrap: 'wrap', gap: 8, marginTop: 6 },
  tag: {
    fontFamily: MONO,
    fontSize: 11,
    color: C.faint,
    borderWidth: 1,
    borderColor: C.line,
    borderRadius: 999,
    paddingHorizontal: 10,
    paddingVertical: 4,
    overflow: 'hidden',
  },
  tagPriority: { color: C.p1, borderColor: C.p1 },
  tagGym: { color: C.gym, borderColor: C.gym },

  buttons: { flexDirection: 'row', gap: 12 },
  big: {
    flex: 1,
    borderWidth: 1,
    borderRadius: 18,
    paddingVertical: 26,
    alignItems: 'center',
    gap: 4,
  },
  bigLetter: { fontFamily: MONO, fontSize: 38, fontWeight: '600' },
  bigLabel: { fontSize: 15, fontWeight: '500' },
  pressed: { opacity: 0.7 },

  section: { fontFamily: MONO, fontSize: 10, letterSpacing: 1.4, color: C.faint, marginTop: 6 },

  progress: { flexDirection: 'row', alignItems: 'center', gap: 12 },
  progressLabel: { width: 46, fontSize: 15, color: C.text },
  pips: { flexDirection: 'row', gap: 5, flex: 1 },
  pip: { flex: 1, height: 8, borderRadius: 4 },
  progressValue: {
    fontFamily: MONO,
    fontSize: 12,
    color: C.muted,
    width: 44,
    textAlign: 'right',
  },

  strip: { flexDirection: 'row', gap: 6 },
  cell: {
    flex: 1,
    alignItems: 'center',
    gap: 6,
    paddingVertical: 10,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: C.line,
    backgroundColor: C.surface,
  },
  cellToday: { borderColor: C.p1 },
  cellDow: { fontFamily: MONO, fontSize: 9, letterSpacing: 0.8, color: C.faint },
  cellDate: { fontSize: 17, fontWeight: '600', color: C.text },
  cellDateToday: { color: C.p1 },
  dot: { width: 18, height: 8, borderRadius: 4, borderWidth: 1 },

  error: { color: '#F09595', fontSize: 14, textAlign: 'center' },
})

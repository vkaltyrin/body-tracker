import { StatusBar } from 'expo-status-bar'
import { useCallback, useEffect, useMemo, useState } from 'react'
import { ActivityIndicator, Pressable, StyleSheet, Text, View } from 'react-native'
import { SafeAreaProvider, SafeAreaView } from 'react-native-safe-area-context'

import * as api from './src/api'
import { addDays, isoDow, key, startOfWeek } from './src/dates'
import { Program } from './src/screens/Program'
import { Today } from './src/screens/Today'
import { C, MONO } from './src/theme'

type Tab = 'today' | 'program'
type Field = 'yoga' | 'gym'

const TABS: { id: Tab; label: string }[] = [
  { id: 'today', label: 'Трекер' },
  { id: 'program', label: 'Программа' },
]

export default function App() {
  const now = useMemo(() => new Date(), [])
  const today = key(now)
  const monday = useMemo(() => startOfWeek(now), [now])

  const [tab, setTab] = useState<Tab>('today')
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

  return (
    <SafeAreaProvider>
      <StatusBar style="light" />
      <SafeAreaView style={s.screen} edges={['top', 'bottom']}>
        {!state || !plan ? (
          <View style={[s.fill, s.center]}>
            {error ? <Text style={s.error}>{error}</Text> : <ActivityIndicator color={C.muted} />}
          </View>
        ) : (
          <View style={s.fill}>
            {tab === 'today' ? (
              <Today
                now={now}
                monday={monday}
                today={today}
                state={state}
                week={week}
                planDay={planDay}
                busy={busy}
                onRefresh={refresh}
                onToggleToday={toggleToday}
                onToggleDay={toggleDay}
              />
            ) : (
              <Program plan={plan} day={planDay} now={now} />
            )}

            {error ? <Text style={s.errorBar}>{error}</Text> : null}

            <View style={s.tabbar}>
              {TABS.map((t) => {
                const active = t.id === tab
                return (
                  <Pressable
                    key={t.id}
                    accessibilityRole="tab"
                    accessibilityState={{ selected: active }}
                    onPress={() => setTab(t.id)}
                    style={({ pressed }) => [s.tab, pressed && s.pressed]}
                  >
                    <View style={[s.tabMark, active && s.tabMarkActive]} />
                    <Text style={[s.tabLabel, active && s.tabLabelActive]}>{t.label}</Text>
                  </Pressable>
                )
              })}
            </View>
          </View>
        )}
      </SafeAreaView>
    </SafeAreaProvider>
  )
}

const s = StyleSheet.create({
  screen: { flex: 1, backgroundColor: C.bg },
  fill: { flex: 1 },
  center: { alignItems: 'center', justifyContent: 'center' },

  tabbar: {
    flexDirection: 'row',
    borderTopWidth: 1,
    borderTopColor: C.line,
    backgroundColor: C.surface,
    paddingTop: 8,
    paddingBottom: 4,
  },
  tab: { flex: 1, alignItems: 'center', gap: 6, paddingVertical: 4 },
  tabMark: { width: 22, height: 3, borderRadius: 2, backgroundColor: 'transparent' },
  tabMarkActive: { backgroundColor: C.p1 },
  tabLabel: { fontFamily: MONO, fontSize: 11, letterSpacing: 0.8, color: C.faint },
  tabLabelActive: { color: C.text },
  pressed: { opacity: 0.6 },

  error: { color: '#F09595', fontSize: 14, textAlign: 'center', paddingHorizontal: 24 },
  errorBar: {
    color: '#F09595',
    fontSize: 13,
    textAlign: 'center',
    paddingVertical: 8,
    paddingHorizontal: 20,
  },
})

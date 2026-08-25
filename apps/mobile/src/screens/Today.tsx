import { Pressable, RefreshControl, ScrollView, StyleSheet, Text, View } from 'react-native'

import type { Entry, PlanDay, Today as TodayState } from '../api'
import { DOW, addDays, key, longDate } from '../dates'
import { C, MONO } from '../theme'

type Field = 'yoga' | 'gym'

export function Today({
  now,
  monday,
  today,
  state,
  week,
  planDay,
  busy,
  onRefresh,
  onToggleToday,
  onToggleDay,
}: {
  now: Date
  monday: Date
  today: string
  state: TodayState
  week: Record<string, Entry>
  planDay: PlanDay | undefined
  busy: boolean
  onRefresh: () => void
  onToggleToday: (field: Field) => void
  onToggleDay: (day: string, field: Field) => void
}) {
  return (
    <ScrollView
      contentContainerStyle={s.content}
      refreshControl={<RefreshControl refreshing={busy} onRefresh={onRefresh} tintColor={C.muted} />}
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
          onPress={() => onToggleToday('yoga')}
        />
        <Big
          label="Зал"
          letter="G"
          on={state.gym_done}
          color={C.gym}
          soft={C.gymSoft}
          onPress={() => onToggleToday('gym')}
        />
      </View>

      <Text style={s.section}>ЦЕЛЬ НЕДЕЛИ</Text>
      <Progress label="Йога" value={state.week.yoga} target={state.target.yoga} color={C.yoga} />
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
              <Dot on={!!e?.yoga} color={C.yoga} onPress={() => onToggleDay(k, 'yoga')} />
              <Dot on={!!e?.gym} color={C.gym} onPress={() => onToggleDay(k, 'gym')} />
            </View>
          )
        })}
      </View>
    </ScrollView>
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
          <View key={i} style={[s.pip, { backgroundColor: i < value ? color : C.line }]} />
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
  content: { padding: 20, paddingBottom: 32, gap: 18 },

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
  progressValue: { fontFamily: MONO, fontSize: 12, color: C.muted, width: 44, textAlign: 'right' },

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
})

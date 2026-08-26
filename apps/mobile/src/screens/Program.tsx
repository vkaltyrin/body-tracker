import { Linking, Pressable, ScrollView, StyleSheet, Text, View } from 'react-native'

import type { Gym, Lesson, Plan, PlanDay, Slot } from '../api'
import { longDate } from '../dates'
import { C, MONO } from '../theme'

/** Лента: что именно делать сегодня и зачем. */
export function Program({ plan, day, now }: { plan: Plan; day: PlanDay | undefined; now: Date }) {
  const byId = new Map(plan.lessons.map((l) => [l.id, l]))
  const goals = plan.goals.filter((g) => day?.goals.includes(g.id))

  if (!day) {
    return (
      <View style={[s.flex, s.center]}>
        <Text style={s.muted}>На этот день программы нет</Text>
      </View>
    )
  }

  return (
    <ScrollView contentContainerStyle={s.content}>
      <Text style={s.eyebrow}>{longDate(now).toUpperCase()}</Text>
      <Text style={s.axis}>{day.axis}</Text>
      <Text style={s.detail}>{day.detail}</Text>

      <Section title="ЦЕЛИ ДНЯ" />
      {goals.map((g) => (
        <View key={g.id} style={s.goal}>
          <View style={[s.goalMark, g.priority === 1 && s.markP1, g.priority === 2 && s.markP2]} />
          <View style={s.flex}>
            <Text style={s.goalTitle}>{g.title}</Text>
            <Text style={s.goalRank}>
              {g.priority ? `Приоритет ${g.priority}` : 'Добиваем'}
            </Text>
          </View>
        </View>
      ))}

      <Section title="ЙОГА" trailing="утро" />
      {day.slots.map((slot, i) => (
        <SlotCard key={`${slot.kind}-${i}`} slot={slot} byId={byId} />
      ))}

      {day.gym ? (
        <>
          <Section title="ЗАЛ" trailing="вечер" />
          <GymCard gym={day.gym} />
        </>
      ) : (
        <>
          <Section title="ЗАЛ" />
          <Text style={s.muted}>Сегодня зала нет — день свободен под приоритет.</Text>
        </>
      )}

      <Text style={s.footer}>{plan.note}</Text>
    </ScrollView>
  )
}

function Section({ title, trailing }: { title: string; trailing?: string }) {
  return (
    <View style={s.section}>
      <Text style={s.sectionTitle}>{title}</Text>
      {trailing ? <Text style={s.sectionTrailing}>{trailing}</Text> : null}
    </View>
  )
}

function SlotCard({ slot, byId }: { slot: Slot; byId: Map<string, Lesson> }) {
  const main = slot.kind === 'main'
  return (
    <View style={[s.card, main && s.cardMain]}>
      <View style={s.cardHead}>
        <Text style={[s.kind, main && s.kindMain]}>{slot.title}</Text>
        <Text style={s.minutes}>{slot.minutes} мин</Text>
      </View>
      <Text style={[s.direction, main && s.directionMain]}>{slot.direction}</Text>
      <View style={s.lessons}>
        {slot.lessons.map((id) => {
          const lesson = byId.get(id)
          if (!lesson) return null
          return <LessonRow key={id} lesson={lesson} />
        })}
      </View>
    </View>
  )
}

function LessonRow({ lesson }: { lesson: Lesson }) {
  return (
    <Pressable
      accessibilityRole="link"
      onPress={() => void Linking.openURL(lesson.url)}
      style={({ pressed }) => [s.lesson, pressed && s.pressed]}
    >
      <Text style={s.lessonTitle} numberOfLines={2}>
        {lesson.title}
      </Text>
      <Text style={s.lessonMinutes}>{lesson.minutes}</Text>
    </Pressable>
  )
}

function GymCard({ gym }: { gym: Gym }) {
  return (
    <View style={[s.card, s.cardGym]}>
      <View style={s.cardHead}>
        <Text style={[s.kind, s.kindGym]}>{gym.session}</Text>
        {gym.optional ? <Text style={s.minutes}>опционально</Text> : null}
      </View>
      <Text style={s.warmup}>Разминка: {gym.warmup}</Text>
      {gym.blocks.map((b, i) => (
        <View key={`${b.tag}-${i}`} style={s.block}>
          <Text style={s.blockTag}>{b.tag}</Text>
          <Text style={s.blockText}>{b.text}</Text>
          <Text style={s.blockScheme}>{b.scheme}</Text>
        </View>
      ))}
      <Text style={s.aim}>{gym.aim}</Text>
    </View>
  )
}

const s = StyleSheet.create({
  flex: { flex: 1 },
  center: { alignItems: 'center', justifyContent: 'center' },
  content: { padding: 20, paddingBottom: 40, gap: 10 },

  eyebrow: { fontFamily: MONO, fontSize: 11, letterSpacing: 1.4, color: C.faint },
  axis: { fontSize: 27, fontWeight: '600', color: C.text, letterSpacing: -0.4 },
  detail: { fontSize: 16, color: C.muted, marginBottom: 4 },

  section: { flexDirection: 'row', alignItems: 'center', gap: 8, marginTop: 18, marginBottom: 2 },
  sectionTitle: { fontFamily: MONO, fontSize: 10, letterSpacing: 1.6, color: C.faint },
  sectionTrailing: {
    fontFamily: MONO,
    fontSize: 10,
    letterSpacing: 1.2,
    color: C.faint,
    opacity: 0.7,
  },

  goal: { flexDirection: 'row', alignItems: 'center', gap: 12, paddingVertical: 7 },
  goalMark: { width: 4, height: 30, borderRadius: 2, backgroundColor: C.line },
  markP1: { backgroundColor: C.p1 },
  markP2: { backgroundColor: C.p2 },
  goalTitle: { fontSize: 16, color: C.text },
  goalRank: { fontFamily: MONO, fontSize: 10, letterSpacing: 0.8, color: C.faint, marginTop: 2 },

  card: {
    backgroundColor: C.surface,
    borderWidth: 1,
    borderColor: C.line,
    borderRadius: 14,
    padding: 14,
    gap: 8,
  },
  cardMain: { borderColor: C.p1 },
  cardGym: { borderColor: C.gym },
  cardHead: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between' },
  kind: { fontFamily: MONO, fontSize: 10, letterSpacing: 1.2, color: C.faint, textTransform: 'uppercase' },
  kindMain: { color: C.p1 },
  kindGym: { color: C.gym, fontSize: 12 },
  minutes: { fontFamily: MONO, fontSize: 11, color: C.faint },
  direction: { fontSize: 15, color: C.muted },
  directionMain: { fontSize: 17, color: C.text, fontWeight: '500' },

  lessons: { gap: 1, marginTop: 2 },
  lesson: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
    paddingVertical: 9,
    borderTopWidth: 1,
    borderTopColor: C.line,
  },
  lessonTitle: { flex: 1, fontSize: 14.5, color: C.yoga },
  lessonMinutes: { fontFamily: MONO, fontSize: 11, color: C.faint },
  pressed: { opacity: 0.55 },

  warmup: { fontSize: 13, color: C.faint, lineHeight: 19 },
  block: { paddingTop: 9, borderTopWidth: 1, borderTopColor: C.line, gap: 2 },
  blockTag: { fontFamily: MONO, fontSize: 9.5, letterSpacing: 1, color: C.faint, textTransform: 'uppercase' },
  blockText: { fontSize: 14.5, color: C.text },
  blockScheme: { fontFamily: MONO, fontSize: 12, color: C.gym },
  aim: { fontSize: 13, color: C.muted, lineHeight: 19, marginTop: 4 },

  muted: { fontSize: 15, color: C.muted },
  footer: {
    fontFamily: MONO,
    fontSize: 10.5,
    letterSpacing: 0.6,
    color: C.faint,
    marginTop: 22,
    lineHeight: 17,
  },
})

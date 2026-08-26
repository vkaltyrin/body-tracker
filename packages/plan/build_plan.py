"""Сборка plan.json.

Держим план в python-скрипте, а не правим JSON руками: уроки переиспользуются
между днями, и ссылаться на них по id надёжнее, чем копировать названия.
Запуск: python3 packages/plan/build_plan.py
"""

import json
from pathlib import Path

SITE = "https://rashyoga.ru"


def video(n: int) -> str:
    return f"{SITE}/video/{n}"


# id → (название, минуты, номер видео)
LESSONS_RAW = {
    # конструктор Хануманасаны
    "hanu-1-1": ("Хануманасана 1.1 Мобилизация", 13, 181),
    "hanu-1-2": ("Хануманасана 1.2 Мобилизация", 12, 182),
    "hanu-1-3": ("Хануманасана 1.3 Мобилизация", 10, 183),
    "hanu-2-1": ("Хануманасана 2.1 Сила", 17, 184),
    "hanu-2-2": ("Хануманасана 2.2 Сила", 14, 185),
    "hanu-3-1": ("Хануманасана 3.1 Амплитуда", 16, 187),
    "hanu-3-2": ("Хануманасана 3.2 Амплитуда", 16, 188),
    # конструктор Самаконасаны
    "sama-1-1": ("Самаконасана 1.1 Мобилизация", 10, 166),
    "sama-1-2": ("Самаконасана 1.2 Мобилизация", 10, 167),
    "sama-1-3": ("Самаконасана 1.3 Мобилизация", 12, 168),
    "sama-3-1": ("Самаконасана 3.1 Амплитуда", 14, 172),
    "sama-3-4": ("Самаконасана 3.4 Амплитуда", 5, 191),
    "sama-3-5": ("Самаконасана 3.5 Амплитуда", 12, 201),
    # шпагаты
    "prod-1": ("Продольное направление 1", 50, 27),
    "prod-2": ("Продольное направление 2", 45, 28),
    "prod-3": ("Продольное направление 3", 51, 29),
    "prod-4": ("Продольное направление 4", 65, 62),
    "prod-fit": ("Продольный шпагат fit", 48, 89),
    "poper-1": ("Поперечное направление 1", 53, 30),
    "poper-2": ("Поперечное направление 2", 52, 31),
    "poper-3": ("Поперечное направление 3", 47, 32),
    "poper-4": ("Поперечное направление 4", 60, 67),
    "poper-fit": ("Поперечный шпагат fit", 47, 90),
    "poper-interval": ("Поперечный в интервалах", 48, 124),
    "tbs-shpagaty-3": ("Подвижность тбс. Шпагаты 3", 66, 116),
    "ladder-uhp": ("Ladder flow УХП", 48, 160),
    # опора на руках
    "zaryadka-6": ("Зарядка 6 — разминка перед стойками", 23, 216),
    "kisti": ("Сильные кисти и предплечья", 32, 115),
    "stoika-1": ("Курс «Стойка на руках» — Урок 1", 40, 74),
    "stoika-2": ("Курс «Стойка на руках» — Урок 2", 36, 75),
    "stoika-3": ("Курс «Стойка на руках» — Урок 3", 41, 76),
    "stabilnaya-stoika": ("Стабильная стойка", 48, 214),
    "pincha-balans": ("Пинча. Баланс, прессап", 38, 119),
    "idealnaya-stoika": ("Идеальная стойка", 28, 190),
    "silovoe-sgibanie": ("Силовое сгибание плеч", 32, 195),
    "stabilnye-lopatki": ("Стабильные лопатки", 50, 205),
    "znakomstvo-pincha": ("Знакомство · Пинча Маюрасана", 14, 229),
    # кор и компрессия
    "ugolok": ("Уголок L-sit", 62, 132),
    "ugly": ("Углы — балансовые углы и straddle", 72, 55),
    "bhujapidasana": ("Каундиниасана, Бхуджапидасана", 18, 23),
    "lolasana": ("Лоласана", 69, 59),
    "znakomstvo-kor": ("Знакомство · Кор", 17, 225),
    "stalnoy-press": ("Стальной пресс", 25, 86),
    "hollow-body": ("Hollow body", 44, 164),
    # прогибы
    "progiby-1": ("Прогибы 1", 53, 33),
    "progiby-2": ("Прогибы 2", 41, 34),
    "kamatkarasana": ("Каматкарасана флоу", 39, 193),
    "ushtrasana": ("Глубокая Уштрасана", 76, 93),
    "kolcevoy": ("Кольцевой захват", 77, 35),
    "koleso": ("Расслабление на колесе", 8, 144),
    # ротация и наклоны
    "yoga-dandasana": ("Йога Дандасана", 67, 85),
    "rotaciya-tbs": ("Ротация тбс", 50, 39),
    "nogi-za-golovoy": ("Ноги за головой", 68, 101),
    "tittibhasana": ("Титтибхасана", 52, 42),
    "myagkaya-naklony": ("Мягкая наклоны, скрутки", 61, 64),
    # мягкое
    "myagkaya-bedra": ("Мягкая проработка бёдер", 40, 43),
    "myagkoe-vytyazhenie": ("Мягкое вытяжение и скрутки", 56, 97),
    "legkie-plechi": ("Лёгкие плечи", 48, 163),
    "passivnaya-nogi": ("Пассивная растяжка ног", 25, 158),
    "shavasana-2": ("Шавасана 2", 11, 114),
    "shavasana-3": ("Шавасана 3", 7, 179),
}

LESSONS = [
    {"id": i, "title": t, "minutes": m, "url": video(n)} for i, (t, m, n) in LESSONS_RAW.items()
]

GOALS = [
    {"id": "naklon-vmeste", "title": "Пашчимоттанасана — ноги вместе", "priority": 1},
    {"id": "naklon-shiroko", "title": "Упавиштха → Титтибхасана", "priority": 1},
    {"id": "hanumanasana", "title": "Полная Хануманасана", "priority": 1},
    {"id": "samakonasana", "title": "Полная Самаконасана", "priority": 2},
    {"id": "nogi-za-golovoy", "title": "Две ноги за головой, лотос", "priority": None},
    {"id": "progiby", "title": "Глубокие прогибы", "priority": None},
    {"id": "stoika", "title": "Стойка на руках и Пинча", "priority": None},
]


def slot(kind, title, minutes, direction, goals, lessons):
    return {
        "kind": kind,
        "title": title,
        "minutes": minutes,
        "direction": direction,
        "goals": goals,
        "lessons": lessons,
    }


def gym(session, optional, warmup, blocks, aim):
    return {
        "session": session,
        "optional": optional,
        "warmup": warmup,
        "blocks": blocks,
        "aim": aim,
    }


DAYS = [
    {
        "dow": 1,
        "axis": "Опора на руках",
        "detail": "стойка + Пинча",
        "priority": None,
        "goals": ["stoika"],
        "slots": [
            slot("warmup", "Разогрев", "15–20", "Кисти и флексия плеча", ["stoika"],
                 ["zaryadka-6", "kisti"]),
            slot("main", "Основной урок", "40–48", "Навык вертикальной опоры", ["stoika"],
                 ["stoika-1", "stoika-2", "stoika-3", "stabilnaya-stoika", "pincha-balans"]),
            slot("filler", "Добор 1", "12–16", "Кор — компрессия, чередуя вместе и широко",
                 ["naklon-vmeste", "naklon-shiroko", "nogi-za-golovoy"],
                 ["ugolok", "lolasana", "ugly", "bhujapidasana"]),
            slot("filler", "Добор 2", "10–13", "ТБС сгибание, мобилизация",
                 ["hanumanasana"], ["hanu-1-1", "hanu-1-2"]),
        ],
        "gym": gym(
            "Lower A", False,
            "bike · вращения тазом · выпады с ротацией · goblet squat с паузой · вис + scap pull-ups · glute bridge",
            [
                {"tag": "навык", "text": "Фронтальный присед", "scheme": "4 × 3–5 · пустой гриф"},
                {"tag": "A", "text": "Присед со штангой + Подтягивания", "scheme": "3 × 5 · 90 + × 6"},
                {"tag": "B", "text": "Зашагивания на тумбу + Махи гирей", "scheme": "8 / ногу · 18 + 3 × 12 · 36"},
                {"tag": "C", "text": "Трисет: аддукторы / hanging leg raise / suitcase carry", "scheme": "12–15 / 10–12 / 30 м · 24"},
                {"tag": "D", "text": "Икры стоя", "scheme": "3 × 12–15"},
                {"tag": "EMOM", "text": "KB swing 12 / bike 12 кал / devil press 5", "scheme": "12 мин"},
            ],
            "Квадрицепс, односторонняя работа, кор, икры. Аддукторы идут в поперечный, hanging leg raise — в компрессию.",
        ),
    },
    {
        "dow": 2,
        "axis": "Задняя цепь: сила",
        "detail": "сила в амплитуде",
        "priority": 1,
        "goals": ["hanumanasana", "naklon-vmeste"],
        "slots": [
            slot("warmup", "Разогрев", "10–13", "ТБС сгибание, мобилизация",
                 ["hanumanasana"], ["hanu-1-2", "hanu-1-3"]),
            slot("main", "Основной урок", "45–48", "Задняя цепь — сила в амплитуде",
                 ["hanumanasana", "naklon-vmeste"], ["prod-fit", "ladder-uhp", "hanu-2-1", "hanu-2-2"]),
            slot("filler", "Добор 1", "12–16", "Кор — компрессия",
                 ["naklon-vmeste", "nogi-za-golovoy"], ["lolasana", "ugolok"]),
            slot("filler", "Добор 2", "10–12", "ТБС отведение, мобилизация",
                 ["samakonasana"], ["sama-1-1", "sama-1-2"]),
        ],
        "gym": None,
    },
    {
        "dow": 3,
        "axis": "Задняя цепь: амплитуда",
        "detail": "продольный",
        "priority": 1,
        "goals": ["hanumanasana"],
        "slots": [
            slot("warmup", "Разогрев", "10–13", "ТБС сгибание и разгибание, мобилизация",
                 ["hanumanasana"], ["hanu-1-1", "hanu-1-3"]),
            slot("main", "Основной урок", "45–50", "Продольный — амплитуда",
                 ["hanumanasana"], ["prod-1", "prod-2", "prod-3", "prod-4", "hanu-3-1", "hanu-3-2"]),
            slot("filler", "Добор 1", "12–16", "Кор — hollow", ["stoika"],
                 ["stalnoy-press", "hollow-body"]),
            slot("filler", "Добор 2", "10–12", "ТБС отведение, амплитуда",
                 ["samakonasana"], ["sama-3-1", "sama-3-4"]),
        ],
        "gym": gym(
            "Upper A", False,
            "bike · band pull-apart · отжимания · вис + scap pull-ups · лёгкие махи · Cuban press 2×8–10",
            [
                {"tag": "A", "text": "Жим штанги лёжа + Горизонтальная тяга", "scheme": "4 × 8 · 55 + 10–12"},
                {"tag": "B", "text": "Жим гантелей стоя + Подтягивания с весом", "scheme": "8–10 · 2×14 + 3 × 6→8"},
                {"tag": "C", "text": "Face pull + Махи в стороны", "scheme": "12–15 + 12–15 · 6–8"},
                {"tag": "D", "text": "Skull crusher + Сгибания на бицепс", "scheme": "4 × 10–12"},
                {"tag": "E", "text": "Разведения на наклонной 30°", "scheme": "3 × 12–15"},
                {"tag": "финиш", "text": "External rotation", "scheme": "2 × 12–15 / руку"},
                {"tag": "EMOM", "text": "KB clean&press 5+5 @16 / бёрпи 8 / bike 12 кал", "scheme": "9 мин"},
            ],
            "Грудь, оверхед, спина, дельты, руки. Вечером ноги не нужны — поэтому под этим днём стоит приоритет 1.",
        ),
    },
    {
        "dow": 4,
        "axis": "Фронтальная",
        "detail": "Самаконасана",
        "priority": 2,
        "goals": ["samakonasana", "naklon-shiroko", "hanumanasana"],
        "slots": [
            slot("warmup", "Разогрев", "10–13", "ТБС отведение и наружная ротация",
                 ["samakonasana"], ["sama-1-1", "sama-1-3"]),
            slot("main", "Основной урок", "47–53", "ТБС отведение: сила → амплитуда",
                 ["samakonasana"], ["poper-1", "poper-2", "poper-3", "poper-4", "poper-fit", "poper-interval"]),
            slot("filler", "Добор 1", "12–16", "Задняя цепь, амплитуда",
                 ["naklon-vmeste", "hanumanasana"], ["hanu-3-1", "hanu-3-2"]),
            # Приводящие уже раскрыты основным уроком — лучший слот недели под
            # сгибание при отведении. Здесь два вектора складываются, а не спорят.
            slot("filler", "Добор 3", "12–15", "Упавиштха → Титтибхасана: сгибание при отведении",
                 ["naklon-shiroko", "samakonasana"], ["poper-3", "tittibhasana", "ugly"]),
            slot("filler", "Добор 2", "10–12", "Плечо — флексия", ["stoika"],
                 ["silovoe-sgibanie", "stabilnye-lopatki"]),
        ],
        "gym": None,
    },
    {
        "dow": 5,
        "axis": "Экстензия",
        "detail": "прогибы",
        "priority": None,
        "goals": ["progiby"],
        "slots": [
            slot("warmup", "Разогрев", "10–13", "Плечо — экстензия, грудной отдел",
                 ["progiby"], ["koleso", "legkie-plechi"]),
            slot("main", "Основной урок", "39–53", "Разгибание позвоночника и ТБС",
                 ["progiby"], ["progiby-1", "progiby-2", "kamatkarasana", "ushtrasana", "kolcevoy"]),
            slot("filler", "Добор 1", "12–16", "Плечо — флексия, опора", ["stoika"],
                 ["znakomstvo-pincha", "idealnaya-stoika"]),
            slot("filler", "Добор 2", "10–12", "ТБС отведение, амплитуда",
                 ["samakonasana"], ["sama-3-5", "sama-3-4"]),
        ],
        "gym": gym(
            "Lower B", False,
            "bike · вращения тазом · выпады с ротацией · glute bridge + румынская с пустым грифом · вис · good morning с палкой",
            [
                {"tag": "навык", "text": "Взятие на грудь", "scheme": "5 × 2–3 · пустой гриф"},
                {"tag": "A", "text": "Становая, лесенка + Подтягивания", "scheme": "70 → 80 → 90 × 5 + × 6"},
                {"tag": "B", "text": "Ягодичный мост", "scheme": "3 × 8 · 80"},
                {"tag": "C", "text": "Румынская тяга, полная амплитуда", "scheme": "4 × 8 · 60"},
                {"tag": "D", "text": "Nordic curls + Jefferson curls", "scheme": "3 × 4–6 + 6–8"},
                {"tag": "E", "text": "Икры на согнутых", "scheme": "3 × 12–15"},
                {"tag": "EMOM", "text": "опционально: трастеры 8 / bike 12 кал / mountain climbers 20", "scheme": "9 мин"},
            ],
            "Взрыв и сила задней цепи в удлинённой позиции. RDL, Nordic и Jefferson curls — прямой вклад в Хануманасану и Пашчимоттанасану.",
        ),
    },
    {
        "dow": 6,
        "axis": "Восстановление",
        "detail": "снятие тонуса",
        "priority": None,
        "goals": ["naklon-vmeste", "naklon-shiroko", "progiby"],
        "slots": [
            slot("main", "Основной урок", "40–56", "Снятие тонуса, пассивная амплитуда",
                 ["naklon-vmeste"], ["myagkaya-bedra", "myagkoe-vytyazhenie", "legkie-plechi"]),
            slot("filler", "Добор 1", "12–25", "Задняя цепь мягко — ноги вместе и широко",
                 ["naklon-vmeste", "naklon-shiroko"], ["passivnaya-nogi", "myagkaya-naklony"]),
            slot("filler", "Добор 2", "8–12", "Пассивный прогиб и шавасана",
                 ["progiby"], ["koleso", "shavasana-3"]),
        ],
        "gym": gym(
            "Upper B", True,
            "bike · shoulder dislocates · wall slides · scap push-ups · вис · Cuban press 2×8–10",
            [
                {"tag": "A", "text": "Армейский жим стоя + Тяга гантели в наклоне", "scheme": "4 × 6–8 · 30 + 10 / руку · 20–22"},
                {"tag": "B", "text": "Жим гантелей на наклонной 30° + Farmer carry", "scheme": "3 × 10–12 · 2×18 + 30 м · 2×24"},
                {"tag": "C", "text": "Махи в стороны + Face pull", "scheme": "4 × 12–15 + 12–15"},
                {"tag": "D", "text": "Пряморучный pulldown", "scheme": "3 × 12–15"},
                {"tag": "E", "text": "Hammer curls + Трицепс pushdown", "scheme": "4 × 10–12"},
                {"tag": "финиш", "text": "External rotation", "scheme": "2 × 12–15 / руку"},
                {"tag": "EMOM", "text": "devil press 5 / bike 12 кал / отжимания 12", "scheme": "9 мин"},
            ],
            "Оверхед штангой, ширина спины, руки. Клапан недели: выпадает первым, когда нужно разгрузиться.",
        ),
    },
    {
        "dow": 7,
        "axis": "Задняя цепь: глубокий наклон",
        "detail": "Пашчимоттанасана",
        "priority": 1,
        "goals": ["naklon-vmeste", "nogi-za-golovoy", "naklon-shiroko"],
        "slots": [
            slot("warmup", "Разогрев", "10–13", "ТБС сгибание, мобилизация",
                 ["naklon-vmeste"], ["hanu-1-1"]),
            slot("main", "Основной урок", "52–66", "Глубокий наклон: пассивная и активная амплитуда",
                 ["naklon-vmeste"], ["myagkaya-naklony", "tittibhasana", "tbs-shpagaty-3"]),
            slot("filler", "Добор 3", "8–10", "Упавиштха пассивно — грудь к полу",
                 ["naklon-shiroko"], ["poper-3"]),
            slot("filler", "Добор 1", "12–16", "ТБС наружная ротация и глубокое сгибание",
                 ["nogi-za-golovoy"], ["yoga-dandasana", "rotaciya-tbs", "nogi-za-golovoy"]),
            slot("filler", "Добор 2", "10–12", "Кор — компрессия и шавасана",
                 ["naklon-vmeste"], ["ugolok", "shavasana-2"]),
        ],
        "gym": None,
    },
]

PLAN = {
    "version": 3,
    "name": "Приоритет: задняя цепь",
    "note": "Йога утром семь дней, зал вечером пн · ср · пт · сб опц.",
    "targets": {"yoga": 7, "gym": 4},
    "priorities": [
        {"rank": 1, "title": "Наклоны · Хануманасана · Пашчимоттанасана · Упавиштха"},
        {"rank": 2, "title": "Самаконасана"},
    ],
    "goals": GOALS,
    "lessons": LESSONS,
    "days": DAYS,
}

if __name__ == "__main__":
    out = Path(__file__).parent / "plan.json"
    out.write_text(json.dumps(PLAN, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    known = {lesson["id"] for lesson in LESSONS}
    used = {i for d in DAYS for s in d["slots"] for i in s["lessons"]}
    missing = used - known
    if missing:
        raise SystemExit(f"Уроки без описания: {sorted(missing)}")
    print(f"{out}: {len(DAYS)} дней, {len(LESSONS)} уроков, лишних ссылок нет")

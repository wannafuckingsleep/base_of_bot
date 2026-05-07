from dataclasses import dataclass
from typing import Optional

_current_platform = "vk"  # дефолт, чтобы не упасть


def set_platform(platform: str) -> None:
    """
    Вызывается один раз при старте конкретного бота (TG/VK).
    """
    global _current_platform
    _current_platform = platform


class EmojiMeta(type):
    def __getattribute__(cls, name: str):
        value = super().__getattribute__(name)

        if isinstance(value, str):
            return value

        if isinstance(value, (list, tuple)) and len(value) >= 2:
            if _current_platform == "vk":
                return value[0]
            if _current_platform == "max":
                return value[0]
            if _current_platform == "tg":
                return value[1]

        return value


@dataclass
class EmojiData:
    emoji: str
    ID: Optional[int] = None

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        if self.ID is None or _current_platform == "vk":
            return f"{self.emoji}"
        if _current_platform == "tg":
            return f'<tg-emoji emoji-id="{self.ID}">{self.emoji}</tg-emoji>'
        return f"{self.emoji}"


class Emoji(metaclass=EmojiMeta):
    toad = EmojiData("🐸", ID=5298596819729684148)
    angry = EmojiData("😡")
    filthy_language = EmojiData("🤬")
    dumb_smile = EmojiData("🙂")
    cry = EmojiData("😭", ID=5453886323003763285)
    laugh = EmojiData("😂")
    shocked_face = EmojiData("🤯")
    cry_with_sweat = EmojiData("😰")
    congratulations = EmojiData("🥳")
    firecracker = EmojiData("🎉")
    tongue_smile = EmojiData("😝")
    cutie = EmojiData("☺️")
    calm = EmojiData("😌")
    whistle = EmojiData("😗")
    kiss = EmojiData("😘")
    astonishment = EmojiData("😧")
    wonder = EmojiData("😳")
    wink = EmojiData("😉")
    sleep = EmojiData("😴")
    cool = EmojiData("😎")
    think = EmojiData("🤔")
    vomit = EmojiData("🤢")
    vomit_do = EmojiData("🤮")
    lovely = EmojiData("🥰")
    scream = EmojiData("😱")
    dizzy = EmojiData("😵", ID=5452022783938669375)
    rolls_eyes = EmojiData("🙄")
    weakness = EmojiData("😖")
    space_invader = EmojiData("👾")
    baby = EmojiData("👶")
    grin = EmojiData("😁")
    horns = EmojiData("🤘")
    crocodile = EmojiData("🐊")
    snow = EmojiData("❄️")
    mask_face = EmojiData("🥸")
    policeman = EmojiData("👮🏻‍♂️")
    monster = EmojiData("👹")
    crown = EmojiData("👑", ID=5296431941464134211)
    alarm = EmojiData("⏰")
    clocks = EmojiData("🕒")
    correct = EmojiData("✅")
    incorrect = empty = EmojiData("❌")
    incorrect_green = EmojiData("❎")
    hourglass = EmojiData("⏳")
    refusal = EmojiData("🙅‍♂️")
    bride = EmojiData("👰‍♀️")
    back = EmojiData("⬅️")
    warning = EmojiData("⚠️")
    ghost = EmojiData("👻")
    info = EmojiData("ℹ️")
    idea = EmojiData("💡")
    heart = EmojiData("❤️")
    bandaged_heart = EmojiData("❤️‍🩹")
    green_heart = EmojiData("💚")
    sparkling_heart = EmojiData("💖", ID=5454316734561398428)
    heart_with_arrow = EmojiData("💘", ID=5454316734561398428)
    swords = EmojiData("⚔️")
    sword = EmojiData("🗡️", ID=5296525765024715045)
    knife = EmojiData("🔪")
    bow = EmojiData("🏹", ID=5296424012954507433)
    dynamite = EmojiData("🧨")
    attack = swords
    shield = EmojiData("🛡️")
    help_man = EmojiData("🙋")
    book = EmojiData("📖")
    books = EmojiData("📚")
    book_yellow = EmojiData("📔")
    plate_with_cutlery = EmojiData("🍽️")
    attention = EmojiData("❗")
    super_attention = EmojiData("‼️")
    question_mark = EmojiData("❓")
    goblet = EmojiData("🏆")
    handshake = EmojiData("🤝")
    cooker = EmojiData("🧑‍🍳")
    hit = EmojiData("👊")
    fire = EmojiData("🔥")
    dance = EmojiData("💃🏻")
    bone = EmojiData("🦴")
    gift = EmojiData("🎁")
    diamond = EmojiData("💎")
    calendar = EmojiData("🗓️")
    calendar_with_date = EmojiData("📆")
    flame = fire
    briefcase = EmojiData("💼", ID=5435965060860091475)
    smirk_cat = EmojiData("😼")
    magnifier = EmojiData("🔍")
    star = EmojiData("⭐️")
    chat = EmojiData("💬")
    human = EmojiData("👤")
    label = EmojiData("🏷")
    key = EmojiData("🔑")
    casino = EmojiData("🎰")
    bank = EmojiData("🏦")
    runner = EmojiData("🏃")
    money_bag = EmojiData("💰")
    yarn = EmojiData("🧶")
    nail_care = EmojiData("💅")
    chick = EmojiData("🐥")
    chick_in_egg = EmojiData("🐣")
    downwards_trend = EmojiData("📉")
    heron_wing = EmojiData("🪽")
    waterlily = EmojiData("🪷")
    fencing = EmojiData("🤺")
    racing_car = EmojiData("🏎")
    hamburger = EmojiData("🍔")
    yammy = EmojiData("😋")
    gear = EmojiData("⚙️")
    megaphone = EmojiData("📣")
    wood = EmojiData("🪵")
    ring = EmojiData("💍")
    palms = EmojiData("🤲")
    boxing_gloves = EmojiData("🥊")
    dancing_couple = EmojiData("👯‍♂️")
    marriage_registry = EmojiData("💒")
    red_mark = EmojiData("📍")
    shiny_stars = EmojiData("✨")
    greet = EmojiData("👋")
    frozen = EmojiData("🥶")
    broken_chain = EmojiData("⛓️‍💥")
    baby_bottle = EmojiData("🍼")
    bouquet = EmojiData("💐")
    band_aid = EmojiData("🩹")
    hook = EmojiData("🪝")
    postcard = EmojiData("💌")
    change_partner = EmojiData("👫")
    please = EmojiData("🙏")
    arena = EmojiData("🏟️")
    broom = EmojiData("🧹")
    bank_card = EmojiData("💳")
    block_in_fire = EmojiData("📛")
    adult_restricted = EmojiData("🔞")
    white_flag = EmojiData("🏳️")
    blood = EmojiData("🩸")
    cigarette = EmojiData("🚬")
    sandglass = EmojiData("⏳")
    swordsman = fencing
    bang = EmojiData("💥")
    quiet_face = EmojiData("🤫")
    backpack = EmojiData("🎒")
    radio = EmojiData("📻")
    pistol = EmojiData("🔫")
    mobile_phone = EmojiData("📱")
    underpants = EmojiData("🩲")
    video_camera = EmojiData("📹")
    headphones = EmojiData("🎧")
    wrestlers = EmojiData("🤼‍♂️")
    abacus = EmojiData("🧮")
    robbery = EmojiData("🥷", ID=5454315218437942739)
    ban = EmojiData("🚫")
    beer = EmojiData("🍻", ID=5296425662221948949)
    wrench = EmojiData("🔧")
    clover_three_leaf = EmojiData("☘️")
    clover_four_leaf = EmojiData("🍀")
    plus = EmojiData("➕")
    minus = EmojiData("➖")
    scissors = EmojiData("✂️")
    cactus = EmojiData("🌵")
    vampire = EmojiData("🧛")
    hedgehog = EmojiData("🦔")
    sun = EmojiData("☀️")
    eyes = EmojiData("👀")
    hand_stop = EmojiData("✋")
    target = EmojiData("🎯")
    name_tag = EmojiData("🏷")
    earth_planet = EmojiData("🌎")
    like = EmojiData("👍")
    dislike = EmojiData("👎")
    pumpkin = EmojiData("🎃")
    fleur_de_lis = EmojiData("⚜️")
    clan_booster = fleur_de_lis
    laptop_worker = EmojiData("👨‍💻")
    cow = EmojiData("🐮")
    bell = EmojiData("🔔")
    trident = EmojiData("🔱")
    crit = EmojiData("💢")
    dirt = EmojiData("🟤")
    reed = EmojiData("🌾")
    snag = EmojiData("🪾")
    heron_beak = EmojiData("🦩")
    lock = EmojiData("🔒")
    unlock = EmojiData("🔓")
    lock_with_key = EmojiData("🔐")
    memo = EmojiData("📝")
    granny = EmojiData("🧓")
    page = EmojiData("📄")
    gang_toads = EmojiData("🐸", ID=5296685980189759015)
    ticket = EmojiData("🎟")

    monkey_with_closed_eyes = EmojiData("🙈")

    achievement_gold = EmojiData("🥇")
    achievement_silver = EmojiData("🥈")
    achievement_bronze = EmojiData("🥉")

    # Флаги
    russia = EmojiData("🇷🇺")
    sphere = EmojiData("🌐")

    # Стрелочки
    arrow_up = EmojiData("⬆️")
    arrow_down = EmojiData("⬇️")
    arrow_left = EmojiData("⬅️")
    arrow_right = EmojiData("➡️")

    # Указатели
    finger_up = EmojiData("👆")
    finger_down = EmojiData("👇")
    finger_left = EmojiData("👈")
    finger_right = EmojiData("👉")

    # Валюта
    money = EmojiData("🐞", ID=5296263840739134899)
    toad_gem = EmojiData("💠")
    donate_money = EmojiData("💎", ID=5300848774162193903)

    # Настроение
    good_mood = EmojiData("🙂", ID=5296741539886700990)
    neutral_mood = EmojiData("😐", ID=5296398230265828815)
    bad_mood = EmojiData("☹️", ID=5296756091235900173)

    # Жаба
    lvl = EmojiData("⭐️", ID=5296379336704694077)
    eat = EmojiData("🍰", ID=5296639654672505967)
    status = EmojiData("👑", ID=5296431941464134211)
    mood = good_mood

    scull = EmojiData("☠️")
    reanimate = EmojiData("🤕")
    poison = scull

    # Снаряжение
    lilies = EmojiData("🥬", ID=5296398191611124658)
    seaweed = EmojiData("🌿", ID=5296390636763650000)
    heron = EmojiData("🦴", ID=5296568611618466159)
    weapon_piece = EmojiData("⚙️", ID=5301202941460388094)
    domination_piece = EmojiData("🪅")
    melee = sword  # Ближний бой
    ranged_combat = bow  # Дальний бой
    school_piece = yarn  # Школьный кусочек

    headgear = EmojiData("🐸", ID=5300898823416092863)  # Наголовник
    armor = EmojiData("🥼", ID=5296776599704736836)  # Нагрудник
    paw_guards = EmojiData("🧤", ID=5296726580515606525)  # Налапники

    booster = EmojiData("🚀")

    # Жабёнок
    authority = cool
    sad = EmojiData("🙁")
    spit = EmojiData("💦")
    candy = EmojiData("🍬")

    # Инвентарь
    fly = EmojiData("🦟", ID=5296264115617044630)
    beatle = EmojiData("🪲", ID=5296634011085478504)
    lollipop = EmojiData("🍭", ID=5296664393684129663)
    heal = EmojiData("💊", ID=5294476979725178181)
    map = EmojiData("🗺", ID=5298697957619571892)
    tape = EmojiData("🧿", ID=5296356255550449398)
    donate_map = EmojiData("🌌", ID=5336993956204943030)
    capsule = EmojiData("🔋", ID=5294506937122069529)
    pendant = EmojiData("📿")

    # Банда
    gang = EmojiData("🏋️", ID=5454076310882104096)
    gang_loyalty = handshake

    # Ограбление
    master_key = EmojiData("🪛", ID=5296702124971827123)
    permit = EmojiData("🔖", ID=5296668035816399358)
    battery = EmojiData("🔋", ID=5296681461884161719)

    puzzle = EmojiData("🧩")
    chain = EmojiData("🔗")
    rock = EmojiData("🪨")
    mask = EmojiData("🎭")
    paper = EmojiData("📃")
    lightning = EmojiData("⚡️")

    lock_food = EmojiData("🔐🍏")
    open_food = EmojiData("🔓🍽️")

    # Игровые классы
    empty_class = EmojiData("⚒️")
    craftsman = EmojiData("👷", ID=5305612197836134016)
    assassin = EmojiData("🦹", ID=5305517528166994552)
    adventurer = EmojiData("🧙", ID=5307732408441802484)

    # Сундуки
    mysterious_chest = monkey_with_closed_eyes
    money_chest = money
    satiety_chest = eat
    weapon_chest = weapon_piece
    random_chest = question_mark

    # Нумерация
    one = EmojiData("1️⃣")
    two = EmojiData("2️⃣")
    three = EmojiData("3️⃣")
    four = EmojiData("4️⃣")
    five = EmojiData("5️⃣")
    six = EmojiData("6️⃣")
    seven = EmojiData("7️⃣")
    eight = EmojiData("8️⃣")
    nine = EmojiData("9️⃣")
    zero = EmojiData("0️⃣")

    clocks_0 = EmojiData("🕛")
    clocks_1 = EmojiData("🕐")
    clocks_2 = EmojiData("🕑")
    clocks_3 = EmojiData("🕒")
    clocks_4 = EmojiData("🕓")
    clocks_5 = EmojiData("🕔")
    clocks_6 = EmojiData("🕕")
    clocks_7 = EmojiData("🕖")
    clocks_8 = EmojiData("🕗")
    clocks_9 = EmojiData("🕘")
    clocks_10 = EmojiData("🕙")
    clocks_11 = EmojiData("🕚")

    # Отображение зоны перехода лиг
    league_up = EmojiData("🔺")
    league_stay = EmojiData("🔹")
    league_down = EmojiData("🔻")
    zone_visibility_delay = EmojiData("🔸")

    # STATEMENTS
    alive_toad = EmojiData("❤️", ID=5454197274341027959)
    dead_toad = EmojiData("😵", ID=5452022783938669375)

    # GARDEN
    seedbed = EmojiData("🪹")

    sprout = EmojiData("🌱")
    young_plant = EmojiData("🌿")
    mature_plant = EmojiData("🍀")

    healthy_plant = EmojiData("❤️")
    affected_plant = EmojiData("❤️‍🩹")
    sick_plant = EmojiData("💔")
    dead_plant = EmojiData("🪾")

    water = EmojiData("💧")
    no_water = EmojiData("🤍")
    watering = EmojiData("🚿")

    pull_out = EmojiData("🚮")

    sunny = EmojiData("☀️")
    clear = EmojiData("🌤️")
    cloudy = EmojiData("☁️")
    rainy = EmojiData("🌧️")
    fog = EmojiData("🌫️")
    new_moon = EmojiData("🌑")
    full_moon = EmojiData("🌕")
    half_moon = EmojiData("🌓")


import asyncio
from datetime import datetime


from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import (
    Message,
    CallbackQuery,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from aiogram.filters import CommandStart, Command

from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

import database



BOT_TOKEN = "ozingizn bot tokenz olib joylashsz"
ADMIN_ID = #admin id qoyiladi

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
router = Router()

dp.include_router(router)





# Dev : @QahramonovK
# Savollar bo‘lsa : Telegram @QahramonovK
# Maxsus buyurtma asosida yaratildi
# Kanalim : @AkazaOrg





# ---------------- ADMIN PANEL ---------------- #

admin_panel = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="*️⃣ qism tahrirlash")],
        [KeyboardButton(text="📊 Statistika"), KeyboardButton(text="✉️ Xabar Yuborish")],
        [KeyboardButton(text="📬 Post tayyorlash")],
        [KeyboardButton(text="🎥anime qoshish"), KeyboardButton(text="📭Tayor Post Yuborish")],
        [KeyboardButton(text="🎥 Seriya qoshish"), KeyboardButton(text="👀Korish Statiskasi")],
        [KeyboardButton(text="📁anime tahrirlash "), KeyboardButton(text="🧾Bitta qismlilar")],
        [KeyboardButton(text="🔎 Foydalanuvchini boshqarish")],
        [KeyboardButton(text="📢Majburiy Azo"), KeyboardButton(text="🎛 "), KeyboardButton(text="📃 xabar yuborish")],
        [KeyboardButton(text="📋 Admin qoshish"), KeyboardButton(text="👤alohida xabar yuborish")],
        [KeyboardButton(text="⚙️ Sozlamalar"), KeyboardButton(text="🗂 bita qismli anime")],
        [KeyboardButton(text="◀️ Orqaga")]
    ],
    resize_keyboard=True
)

# ---------------- ADMIN TEKSHIRISH ---------------- #

drouter = Router()

def admin_only(func):
    async def wrapper(message: Message, *args, **kwargs):
        if message.from_user.id != ADMIN_ID:
            return
        await func(message, *args, **kwargs)
    return wrapper

# ---------------- START ---------------- #
@router.message(CommandStart())
async def start(message: Message):
    database.add_user(message.from_user.id)

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✏️ Bot haqida", callback_data="about"),
                InlineKeyboardButton(text="🔒 Yopish", callback_data="close")
            ]
        ]
    )

    text = """
Bu bot orqali kanaldagi animelarni yuklab olishingiz mumkin

❗️Botga habar yozmang❗️
"""

    await message.answer(text, reply_markup=kb)


# ---------------- ABOUT ---------------- #
@router.callback_query(F.data == "about")
async def about(callback: CallbackQuery):
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="👨‍💻 Yordam", callback_data="help"),
                InlineKeyboardButton(text="🔒 Yopish", callback_data="close")
            ]
        ]
    )

    text = """
Botni ishlatishni bilmaganlar uchun!
❏ Botni ishlatish qo'llanmasi:
    1. Kanallarga obuna boling!
    2. Tekshirish Tugmasini bosing ✅
    3. Kanaldagi anime post past qismidagi yuklab olish tugmasini bosing

👨‍💻 Yaratuvchi @Sukine
"""

    await callback.message.edit_text(text, reply_markup=kb)


# ---------------- HELP ---------------- #
@router.callback_query(F.data == "help")
async def help_cmd(callback: CallbackQuery):
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔒 Yopish", callback_data="close")]
        ]
    )

    text = """
Admin: @Sukinari
Asosiy kanal: @Aniconuz
Reklama: @Aniconuz_reklama
Chat: @Eto_anime_chat
"""

    await callback.message.edit_text(text, reply_markup=kb)

# ---------------- CLOSE ---------------- #

@dp.callback_query(F.data == "close")
async def close(callback: CallbackQuery):

    await callback.message.delete()


# ---------------- ADMIN PANEL ---------------- #

@dp.message(Command("admin"))
@admin_only
async def admin_panel_show(message: Message):

    await message.answer("👑 ADMIN PANEL", reply_markup=admin_panel)


# ---------------- STATISTIKA ---------------- #

@dp.message(F.text == "📊 Statistika")
@admin_only
async def show_stats(message: Message):

    total_users = database.get_users_count()
    anime_count = database.get_anime_count()

    users_1day = database.get_users_count_days(1)
    users_7days = database.get_users_count_days(7)
    users_31days = database.get_users_count_days(31)

    text = f"""
📊 STATISTIKA

👥 Jami userlar: {total_users}

1 kun: {users_1day}
7 kun: {users_7days}
31 kun: {users_31days}

🎬 Animelar: {anime_count}

🕒 {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}
"""

    await message.answer(text)


# ---------------- BROADCAST ---------------- #

@dp.message(F.text == "✉️ Xabar Yuborish")
@admin_only
async def start_broadcast(message: Message):

    database.set_state(message.from_user.id, "broadcast")

    await message.answer("📢 Yuboriladigan xabarni yozing")


@dp.message()
@admin_only
async def send_broadcast(message: Message):

    state = database.get_state(message.from_user.id)

    if state == "broadcast":

        users = database.get_users()

        success = 0
        fail = 0

        for user in users:

            try:
                await bot.send_message(user[0], message.text)
                success += 1
            except:
                fail += 1

        database.clear_state(message.from_user.id)

        await message.answer(
            f"✔️ Yuborildi: {success}\n❌ Yuborilmadi: {fail}"
)


# ---------------- Anime qoshish ---------------- #


class AnimeAdd(StatesGroup):
    waiting_for_title = State()
    waiting_for_genre = State()
    waiting_for_votes = State()
    waiting_for_year = State()


# Start adding anime
@dp.message(F.text == "🎥anime qoshish")
@admin_only
async def add_anime_start(message: Message, state: FSMContext):
    await message.answer("🎬 Anime nomini kiriting:")
    await state.set_state(AnimeAdd.waiting_for_title)


@dp.message(AnimeAdd.waiting_for_title)
@admin_only
async def add_anime_title(message: Message, state: FSMContext):
    database.save_temp_data(message.from_user.id, "title", message.text)
    await message.answer("📅 Janr kiriting:")
    await state.set_state(AnimeAdd.waiting_for_genre)


@dp.message(AnimeAdd.waiting_for_genre)
@admin_only
async def add_anime_genre(message: Message, state: FSMContext):
    database.save_temp_data(message.from_user.id, "genre", message.text)
    await message.answer("🗳 Kim ovoz berganini yozing (masalan: Uzbek tilida yoki Rus tilida):")
    await state.set_state(AnimeAdd.waiting_for_votes)


@dp.message(AnimeAdd.waiting_for_votes)
@admin_only
async def add_anime_votes(message: Message, state: FSMContext):
    database.save_temp_data(message.from_user.id, "votes", message.text)
    await message.answer("📆 Yil kiriting:")
    await state.set_state(AnimeAdd.waiting_for_year)


@dp.message(AnimeAdd.waiting_for_year)
@admin_only
async def add_anime_year(message: Message, state: FSMContext):
    database.save_temp_data(message.from_user.id, "year", message.text)

    # Temp datadan olish
    title = database.get_temp_data(message.from_user.id, "title")
    genre = database.get_temp_data(message.from_user.id, "genre")
    votes = database.get_temp_data(message.from_user.id, "votes")
    year = database.get_temp_data(message.from_user.id, "year")

    # Anime saqlash
    database.save_anime(title, genre, votes, year)

    await message.answer("✅ Anime qo'shildi!", reply_markup=admin_panel)
    await state.clear()

# ---------------- qism qoshish ---------------- #


class EpisodeAdd(StatesGroup):
    waiting_for_anime_id = State()
    waiting_for_media = State()

@dp.message(EpisodeAdd.waiting_for_anime_id)
@admin_only
async def process_anime_id(message: Message, state: FSMContext):
    anime_id = message.text

    # Database dan anime ma'lumotlarini olish
    anime = database.get_anime_by_id(anime_id)  # database.py da bo'lishi kerak
    if not anime:
        await message.answer("❌ Anime topilmadi! Iltimos, to‘g‘ri ID kiriting.")
        return

    # Joriy qismlar soni
    current_episodes = database.get_episodes_count(anime_id)

    # Keyingi qism raqami
    next_episode_number = current_episodes + 1

    # Adminga xabar yuborish
    text = f"""
✅ Anime topildi:
🏷 Nomi: {anime['title']}
🎙 Ovoz: {anime['votes_info']}
📊 Joriy qismlar: {current_episodes}
➡️ Keyingi qism: {next_episode_number}                                                                                                              
🎬 Endi qismni video sifatida yuboring:
"""

    await message.answer(text)

    # FSM data saqlash
    await state.update_data(anime_id=anime_id, next_episode_number=next_episode_number)
    await state.set_state(EpisodeAdd.waiting_for_media)  # admin video yuborishi uchun

    
# ---------------- Tayyor post yuborish ---------------- #


class PostSend(StatesGroup):
    waiting_for_anime_id = State()
    waiting_for_channels = State()
    waiting_for_confirmation = State()


@dp.message(F.text == "📭Tayor Post Yuborish")
@admin_only
async def start_post(message: Message, state: FSMContext):
    await message.answer("🆔 Post yuborish uchun anime ID sini kiriting:")
    await state.set_state(PostSend.waiting_for_anime_id)


@dp.message(PostSend.waiting_for_anime_id)
async def process_post_anime_id(message: Message, state: FSMContext):
    anime_id = message.text
    anime = database.get_anime_by_id(anime_id)

    if not anime:
        await message.answer("❌ Anime topilmadi! Iltimos, to‘g‘ri ID kiriting.")
        return

    await message.answer(f"✅ Anime topildi:\nID: {anime['id']}\n🏷 Nomi: {anime['title']}")
    await message.answer(
        "📢 Endi post yubormoqchi bo'lgan kanal linklarini vergul bilan ajratib yuboring:\n\n"
        "• Bitta kanal: @AkazOrG\n"
        "• Bir nechta kanal: @AniEnzen, @animelar_uzbekchasi, @uchinchi_kanal\n"
        "(Bot kanalda admin bo‘lishi kerak)"
    )

    await state.update_data(anime_id=anime_id)
    await state.set_state(PostSend.waiting_for_channels)


@dp.message(PostSend.waiting_for_channels)
async def process_channels(message: Message, state: FSMContext):
    channels = [c.strip() for c in message.text.split(",")]
    valid_channels = [c for c in channels if c.startswith("@")]

    if not valid_channels:
        await message.answer("❌ Hech qanday to‘g‘ri kanal topilmadi, qayta kiriting:")
        return

    await state.update_data(channels=valid_channels)

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Tasdiqlash", callback_data="confirm_post"),
            InlineKeyboardButton(text="❌ Rad etish", callback_data="cancel_post"),
        ]
    ])

    text = "✅ Topilgan kanallar:\n" + "\n".join(f"• {c}" for c in valid_channels)
    text += f"\n\n📊 Jami: {len(valid_channels)} ta kanal\n\n⚠️ Postni barcha kanallarga yuborishni tasdiqlaysizmi?"

    await message.answer(text, reply_markup=kb)
    await state.set_state(PostSend.waiting_for_confirmation)


@dp.callback_query(F.data == "confirm_post")
async def confirm_post(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    anime_id = data.get("anime_id")
    channels = data.get("channels", [])

    anime = database.get_anime_by_id(anime_id)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎬 TOMOSHA QILISH", url="https://t.me/your_channel")]
    ])

    text = (
        f"🎬 {anime['title']}\n"
        f"📂 Janr: {anime.get('description', 'Noma\'lum')}\n"
        f"🎙 Ovoz: {anime.get('votes_info', 'Noma\'lum')}\n"
        f"📢 Post kanallarga yuborildi!"
    )

    # Postni barcha kanallarga yuborish
    for channel in channels:
        if database.bot_is_admin(channel):
            try:
                await bot.send_message(chat_id=channel, text=text, reply_markup=kb)
            except:
                await callback.message.answer(f"❌ {channel} ga yuborilmadi!")
        else:
            await callback.message.answer(f"❌ Bot {channel} kanalida admin emas!")

    await callback.message.answer("✅ Post yuborildi!")
    await state.clear()


@dp.callback_query(F.data == "cancel_post")
async def cancel_post(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("❌ Post yuborish bekor qilindi. Admin panelga qaytish.")
    await state.clear()


    # ---------------- qism tahrirlash ---------------- #

class EpisodeEdit(StatesGroup):
    waiting_for_anime_name = State()
    waiting_for_episode_number = State()
    waiting_for_new_media = State()


@router.message(F.text == "🔄 Qism tahrirlash")
@admin_only
async def start_edit_episode(message: Message, state: FSMContext):
    await message.answer("🔄 Tahrirlash kerak bo'lgan anime nomini yuboring !")
    await state.set_state(EpisodeEdit.waiting_for_anime_name)


@router.message(EpisodeEdit.waiting_for_anime_name)
async def process_anime_name(message: Message, state: FSMContext):
    anime_name = message.text
    anime = database.get_anime_by_name(anime_name)
    if not anime:
        await message.answer("❌ Anime topilmadi! Iltimos, to‘g‘ri nom kiriting.")
        return

    episode_count = database.get_episodes_count(anime['id'])
    status = "Tugal" if episode_count == anime['total_episodes'] else "Davom etmoqda"

    text = f"""
🆔 : {anime['id']}
--------------------
🏷 Nomi : {anime['title']}
📑 Janri : {anime['description']}
🎙 Ovoz beruvchi : {anime['votes_info']}
--------------------
🎞 Seriyalar soni : {episode_count}
🎥 Filmlar soni : {anime.get('movies_count', 0)}
--------------------
💬 Tili : {anime.get('language', '🇺🇿Ozbekcha')}
--------------------
#️⃣ Teg : {anime.get('tag', anime['title'])}
📉 Status : {status}
👁‍🗨 Ko'rishlar : {anime.get('views', 0)}
--------------------
📝 Qaysi qismni tahrirlamoqchisiz? Qism raqamini yuboring:
"""

    if anime.get('media'):
        if anime['media'].startswith("photo:"):
            file_id = anime['media'].split("photo:")[1]
            await message.answer_photo(file_id, caption=text)
        elif anime['media'].startswith("video:"):
            file_id = anime['media'].split("video:")[1]
            await message.answer_video(file_id, caption=text)
        else:
            await message.answer(text)
    else:
        await message.answer(text)

    await state.update_data(anime_id=anime['id'])
    await state.set_state(EpisodeEdit.waiting_for_episode_number)


@router.message(EpisodeEdit.waiting_for_episode_number)
async def process_episode_number(message: Message, state: FSMContext):
    episode_number = message.text
    data = await state.get_data()
    anime_id = data['anime_id']

    episode = database.get_episode(anime_id, episode_number)
    if not episode:
        await message.answer("❌ Bu qism topilmadi!")
        return

    await message.answer(f"✅ {episode_number}-qism topildi. Endi yangi video yuboring:")
    await state.update_data(episode_number=episode_number)
    await state.set_state(EpisodeEdit.waiting_for_new_media)


@router.message(EpisodeEdit.waiting_for_new_media)
async def process_new_media(message: Message, state: FSMContext):
    data = await state.get_data()
    anime_id = data['anime_id']
    episode_number = data['episode_number']
    media = None

    if message.video:
        media = f"video:{message.video.file_id}"
    elif message.photo:
        media = f"photo:{message.photo[-1].file_id}"
    elif message.text.lower() != "pass":
        media = message.text

    database.update_episode_media(anime_id, episode_number, media)

    await message.answer(f"✅ {episode_number}-qism yangilandi!")
    await state.clear()



      # ---------------- korish statiskasi  ---------------- #


router = Router()

@router.message(F.text == "👀Korish Statiskasi")
@admin_only
async def view_stats(message: Message):
    # Eng ko'p ko‘rilgan animelarni database dan olish
    top_animes = database.get_top_viewed_animes(limit=20)
    total_views = database.get_total_views()
    total_animes = database.get_anime_count()
    avg_views = total_views // total_animes if total_animes > 0 else 0

    text = "📊 Eng ko'p ko'rilgan animelar:\n\n"
    for idx, anime in enumerate(top_animes, start=1):
        text += f"{idx}. {anime['title']} — {anime['views']} marta\n—————————————\n"

    text += f"\n📈 Umumiy statistikalar:\n"
    text += f"• Jami ko'rishlar: {total_views}\n"
    text += f"• Animelar soni: {total_animes}\n"
    text += f"• O'rtacha ko'rishlar: {avg_views}"

    await message.answer(text)

 # ---------------- bitta qismlilar   ---------------- #

router = Router()

@router.message(F.text == "🧾Bitta qismlilar")
@admin_only
async def single_episode_list(message: Message):
    # Database dan bitta qismli animelar
    animes = database.get_single_episode_animes()
    
    if not animes:
        await message.answer("❌ Bitta qismli anime topilmadi.")
        return

    for anime in animes:
        text = f"""
🏷 Nom: {anime['title']} (Qism 1)
🆔 ID: {anime['id']}
📺 Kanal: {anime['channel']}
📊 Ko'rishlar: {anime['views']}
⏰ Sana: {anime['upload_date']}
"""
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="✏️ Nomi tahrirlash", callback_data=f"edit_name_{anime['id']}"),
                InlineKeyboardButton(text="🎬 Video almashtirish", callback_data=f"edit_video_{anime['id']}")
            ],
            [
                InlineKeyboardButton(text="📤 Boshqa kanalga joylash", callback_data=f"move_channel_{anime['id']}"),
                InlineKeyboardButton(text="❌ O‘chirish", callback_data=f"delete_{anime['id']}")
            ],
            [
                InlineKeyboardButton(text="◀️ Orqaga", callback_data="admin_panel_back")
            ]
        ])
        await message.answer(text, reply_markup=kb)


 # ---------------- majburiy azo  ---------------- #

router = Router()

class MandatorySubs(StatesGroup):
    waiting_for_channel_username = State()


@router.message(F.text == "📢Majburiy Azo")
@admin_only
async def mandatory_subs_start(message: Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔐 Majburiy obunalar", callback_data="mandatory_add")],
        [InlineKeyboardButton(text="⚡ Zayafka kanal", callback_data="zayafka_channel")],
        [InlineKeyboardButton(text="◀️ Orqaga", callback_data="admin_panel_back")]
    ])
    await message.answer("Quyidagilardan birini tanlang:", reply_markup=kb)


@router.callback_query()
async def mandatory_cb(callback: CallbackQuery, state: FSMContext):
    data = callback.data

    if data == "mandatory_add":
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="➕ Qo‘shish", callback_data="mandatory_add_channel")],
            [InlineKeyboardButton(text="📋 Ro‘yxat", callback_data="mandatory_list")],
            [InlineKeyboardButton(text="◀️ Orqaga", callback_data="admin_panel_back")]
        ])
        await callback.message.answer(
            "🔐 Majburiy obunalarni sozlash bo‘limidasiz:\nPasda keyboard: Qo‘shish / Ro‘yxat",
            reply_markup=kb
        )

    elif data == "mandatory_add_channel":
        await callback.message.answer("🆔 Kanal username sini yuboring (bot admin bo‘lishi kerak):")
        await state.set_state(MandatorySubs.waiting_for_channel_username)

    elif data == "mandatory_list":
        channels = database.get_mandatory_channels()
        if not channels:
            await callback.message.answer("❌ Hech qanday majburiy kanal yo‘q.")
            return
        for idx, ch in enumerate(channels, start=1):
            kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="❌ O‘chirish", callback_data=f"mandatory_delete_{ch['id']}")]
            ])
            await callback.message.answer(
                f"{idx}. {ch['username']}\nUlangan kanallar soni: {len(channels)}",
                reply_markup=kb
            )

    elif data.startswith("mandatory_delete_"):
        ch_id = int(data.split("_")[2])
        database.delete_mandatory_channel(ch_id)
        await callback.message.answer("✅ Kanal majburiy obunalardan o‘chirildi.")


@router.message(MandatorySubs.waiting_for_channel_username)
async def add_mandatory_channel(message: Message, state: FSMContext):
    username = message.text.strip()
    
    # Tekshirish: @ bilan boshlanishi
    if not username.startswith("@"):
        await message.answer("❌ To‘g‘ri username kiriting, @ bilan boshlansin")
        return
    
    # Bot adminligini tekshirish
    if not database.bot_is_admin(username):
        await message.answer("❌ Bot bu kanalda admin emas!")
        return

    database.add_mandatory_channel(username)
    await message.answer(f"✅ Kanal {username} majburiy obunalarga qo‘shildi!")
    await state.clear()


router = Router()

# ---------------- States ---------------- #
class AdminManage(StatesGroup):
    waiting_for_add_id = State()
    waiting_for_remove_id = State()

# ---------------- Admin only decorator ---------------- #
def admin_only(func):
    async def wrapper(message: Message | CallbackQuery, *args, **kwargs):
        user_id = message.from_user.id
        if user_id != ADMIN_ID:  # ADMIN_ID ni o‘zingiz aniqlang
            return
        await func(message, *args, **kwargs)
    return wrapper

# ---------------- Admin Panel ---------------- #
@router.message(F.text == "📋 Admin qoshish")
@admin_only
async def admin_manage_panel(message: Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Admin qo‘shish", callback_data="admin_add")],
        [InlineKeyboardButton(text="📋 Ro‘yxat", callback_data="admin_list")],
        [InlineKeyboardButton(text="➖ Admin olib tashlash", callback_data="admin_remove")],
        [InlineKeyboardButton(text="◀️ Orqaga", callback_data="admin_panel_back")]
    ])
    await message.answer("Adminlarni boshqarish bo‘limi:", reply_markup=kb)

# ---------------- Callback Query Handler ---------------- #
@router.callback_query()
@admin_only
async def handle_admin_cb(callback: CallbackQuery, state: FSMContext):
    data = callback.data

    if data == "admin_add":
        await callback.message.answer("🆔 Admin qo‘shish uchun foydalanuvchi ID sini kiriting:")
        await state.set_state(AdminManage.waiting_for_add_id)

    elif data == "admin_list":
        admins = database.get_admins()  # Sizning database.py dan
        text = "👮 Adminlar ro'yxati:\n\n"
        for admin in admins:
            text += f"• {admin['id']} — {admin['username']}\n"
        await callback.message.answer(text)

    elif data == "admin_remove":
        await callback.message.answer("🆔 Adminlikdan olib tashlash uchun ID kiriting:")
        await state.set_state(AdminManage.waiting_for_remove_id)

    elif data == "admin_panel_back":
        await callback.message.answer("👑 Admin panelga qaytish", reply_markup=admin_panel)

# ---------------- Qo‘shish / Olib tashlash handlerlari ---------------- #
@router.message(AdminManage.waiting_for_add_id)
@admin_only
async def add_admin(message: Message, state: FSMContext):
    try:
        user_id = int(message.text)
        database.add_admin(user_id)
        await message.answer(f"✅ Foydalanuvchi ID {user_id} admin qilindi!")
    except ValueError:
        await message.answer("❌ Iltimos, to‘g‘ri raqam kiriting!")
    await state.clear()

@router.message(AdminManage.waiting_for_remove_id)
@admin_only
async def remove_admin(message: Message, state: FSMContext):
    try:
        user_id = int(message.text)
        database.remove_admin(user_id)
        await message.answer(f"❌ Foydalanuvchi ID {user_id} adminlikdan olindi!")
    except ValueError:
        await message.answer("❌ Iltimos, to‘g‘ri raqam kiriting!")
    await state.clear()

# ---------------- Alohida xabar yuborish ---------------- #
router = Router()

# ---------------- States ---------------- #
class PrivateMessage(StatesGroup):  
    waiting_for_user_id = State()
    waiting_for_message = State()
    waiting_for_confirmation = State()

# ---------------- Alohida xabar yuborish ---------------- #
@router.message(F.text == "👤alohida xabar yuborish")
@admin_only
async def private_message_start(message: Message, state: FSMContext):
    await message.answer("💬 Xabar yuborish uchun foydalanuvchi ID sini kiriting:")
    await state.set_state(PrivateMessage.waiting_for_user_id)

@router.message(PrivateMessage.waiting_for_user_id)
@admin_only
async def private_message_user(message: Message, state: FSMContext):
    try:
        user_id = int(message.text)
        user = database.get_user_by_id(user_id)
        if not user:
            await message.answer("❌ Foydalanuvchi topilmadi! Iltimos, to‘g‘ri ID kiriting.")
            return

        text = f"""
✅ Foydalanuvchi topildi:

🆔: {user['id']}
👤 Username: {user['username']}
---------------
💬 Til: {user['lang']}
---------------
📌 Adminlik: {'Ha' if user['is_admin'] else 'Yo‘q'}
"""
        await message.answer(text)
        await message.answer("❗ Ushbu foydalanuvchiga yuborish uchun xabar kiriting !")
        await state.update_data(user_id=user_id)
        await state.set_state(PrivateMessage.waiting_for_message)
    except ValueError:
        await message.answer("❌ Iltimos, to‘g‘ri raqam kiriting!")

@router.message(PrivateMessage.waiting_for_message)
@admin_only
async def private_message_input(message: Message, state: FSMContext):
    await state.update_data(message_text=message.text)

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Tasdiqlash", callback_data="private_msg_confirm")],
        [InlineKeyboardButton(text="❌ Rad etish", callback_data="private_msg_cancel")]
    ])
    await message.answer("Xabaringizni tasdiqlaysizmi?", reply_markup=kb)
    await state.set_state(PrivateMessage.waiting_for_confirmation)

@router.callback_query(PrivateMessage.waiting_for_confirmation)
@admin_only
async def private_message_confirm(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user_id = data.get("user_id")
    text = data.get("message_text")

    if callback.data == "private_msg_confirm":
        try:
            await bot.send_message(user_id, text)
            await callback.message.answer("✅ Xabar foydalanuvchiga yuborildi!")
        except:
            await callback.message.answer("❌ Xabar yuborilmadi!")
    elif callback.data == "private_msg_cancel":
        await callback.message.answer("❌ Xabar yuborish bekor qilindi.")

    await state.clear()

    # ---------------- Tayor post yuborish ---------------- #


router = Router()

class PreparePost(StatesGroup):
    waiting_for_anime_id = State()
    waiting_for_media = State()
    waiting_for_caption = State()
    waiting_for_buttons = State()


@router.message(F.text == "📭Tayor Post Yuborish")
@admin_only
async def prepare_post_start(message: Message, state: FSMContext):
    await message.answer("🆔 Post yuborish uchun anime ID sini kiriting:")
    await state.set_state(PreparePost.waiting_for_anime_id)


@router.message(PreparePost.waiting_for_anime_id)
@admin_only
async def process_anime_id(message: Message, state: FSMContext):
    anime_id = message.text
    anime = database.get_anime_by_id(anime_id)
    if not anime:
        await message.answer("❌ Anime topilmadi! Iltimos, to‘g‘ri ID kiriting.")
        return
    await state.update_data(anime=anime)
    await message.answer("🖼️ Rasm yoki video yuboring!")
    await state.set_state(PreparePost.waiting_for_media)


@router.message(PreparePost.waiting_for_media, F.content_type.in_({"photo", "video"}))
@admin_only
async def process_media(message: Message, state: FSMContext):
    media = message.photo[-1].file_id if message.photo else message.video.file_id
    media_type = "photo" if message.photo else "video"
    await state.update_data(media=media, media_type=media_type)
    await message.answer(
        "📒 Post uchun tavsif yuboring!\nAgar tavsif kiritishni hohlamasangiz 'Kiritishni hohlamayman' tugmasini bosing."
    )
    await state.set_state(PreparePost.waiting_for_caption)


@router.message(PreparePost.waiting_for_caption)
@admin_only
async def process_caption(message: Message, state: FSMContext):
    caption = "" if message.text.lower() == "kiritishni hohlamayman" else message.text
    await state.update_data(caption=caption)
    await message.answer(
        "🎛️ Tugmalarni yuboring.\nNa'muna:\nTomosha qilish => https://t.me/AkazaOrg\nHar bir tugma alohida qatorda bo‘lsin."
    )
    await state.set_state(PreparePost.waiting_for_buttons)


@router.message(PreparePost.waiting_for_buttons)
@admin_only
async def process_buttons(message: Message, state: FSMContext):
    data = await state.get_data()
    anime = data["anime"]
    media = data["media"]
    media_type = data["media_type"]
    caption = data["caption"]

    # Tugmalarni yaratish
    buttons = []
    for line in message.text.split("\n"):
        if "=>" in line:
            text, url = line.split("=>")
            buttons.append(InlineKeyboardButton(text=text.strip(), url=url.strip()))
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(*buttons)

    # Kanallar ro'yxati
    channel_list = database.get_post_channels(anime['id'])
    for channel in channel_list:
        if not database.bot_is_admin(channel):
            await message.answer(
                f"❌ Bot kanalda admin emas!\nKanal: {channel}\nIltimos, botni kanalga admin qiling va post qo'shish huquqini bering."
            )
            continue

        try:
            if media_type == "photo":
                await bot.send_photo(chat_id=channel, photo=media, caption=f"{anime['title']}\n{caption}", reply_markup=kb)
            else:
                await bot.send_video(chat_id=channel, video=media, caption=f"{anime['title']}\n{caption}", reply_markup=kb)
        except:
            await message.answer(f"❌ Post {channel} ga yuborilmadi!")

    await message.answer("✅ Post barcha kanallarga yuborildi!")
    await state.clear()

     # ---------------- anime tahrirlash ---------------- #
router = Router()

# ---------------- States ---------------- #
class AnimeEdit(StatesGroup):
    waiting_for_id = State()
    waiting_for_field = State()

# ---------------- Anime tahrirlash boshi ---------------- #
@router.message(F.text == "📁anime tahrirlash")
@admin_only
async def edit_anime_start(message: Message, state: FSMContext):
    await message.answer("✏️ Tahrirlash kerak bo'lgan anime nomini yuboring !")
    await state.set_state(AnimeEdit.waiting_for_id)

# ---------------- Anime ma'lumotlarini olish ---------------- #
@router.message(AnimeEdit.waiting_for_id)
@admin_only
async def process_anime_id(message: Message, state: FSMContext):
    anime = database.get_anime_by_name_or_id(message.text)
    if not anime:
        await message.answer("❌ Anime topilmadi! Iltimos, to‘g‘ri nom yoki ID kiriting.")
        return

    text = f"""
🆔 : {anime['id']}
--------------------
🏷 Nomi : {anime['title']}
📑 Janri : {anime['genre']}
🎙 Ovoz beruvchi : {anime['votes_info']}
--------------------
🎞 Seriyalar soni : {anime['episodes_count']}
🎥 Filmlar soni : {anime['movies_count']}
--------------------
💬 Tili : {anime['lang']}
#️⃣ Teg : {anime['tag']}
📉 Status : {anime['status']}
👁‍🗨 Ko'rishlar : {anime['views']}
"""
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Haqidani tahrirlash", callback_data="edit_story")],
        [InlineKeyboardButton(text="🏷 Nomin tahrirlash", callback_data="edit_title")],
        [InlineKeyboardButton(text="🎬 Treylerni o‘zgartirish", callback_data="edit_trailer")],
        [InlineKeyboardButton(text="📑 Janr tahrirlash", callback_data="edit_genre")],
        [InlineKeyboardButton(text="🎙 Fandub tahrirlash", callback_data="edit_votes")],
        [InlineKeyboardButton(text="💬 Tilini tahrirlash", callback_data="edit_lang")],
        [InlineKeyboardButton(text="#️⃣ Tegni tahrirlash", callback_data="edit_tag")],
        [InlineKeyboardButton(text="❌ Animeni o‘chirish", callback_data="delete_anime")],
        [InlineKeyboardButton(text="◀️ Orqaga", callback_data="back_to_admin_panel")]
    ])
    await state.update_data(anime_id=anime['id'])
    await message.answer(text, reply_markup=kb)

# ---------------- Callback query handler ---------------- #
@router.callback_query()
@admin_only
async def edit_anime_callback(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    anime_id = data.get("anime_id")

    if callback.data == "edit_title":
        await callback.message.answer("🏷 Yangi nomni kiriting:")
        await state.set_state(AnimeEdit.waiting_for_field)
        await state.update_data(field="title")
    elif callback.data == "edit_genre":
        await callback.message.answer("📑 Yangi janrni kiriting:")
        await state.set_state(AnimeEdit.waiting_for_field)
        await state.update_data(field="genre")
    elif callback.data == "edit_votes":
        await callback.message.answer("🎙 Yangi ovoz beruvchi nomini kiriting:")
        await state.set_state(AnimeEdit.waiting_for_field)
        await state.update_data(field="votes_info")
    elif callback.data == "edit_lang":
        await callback.message.answer("💬 Yangi tilni kiriting:")
        await state.set_state(AnimeEdit.waiting_for_field)
        await state.update_data(field="lang")
    elif callback.data == "edit_tag":
        await callback.message.answer("#️⃣ Yangi tagni kiriting:")
        await state.set_state(AnimeEdit.waiting_for_field)
        await state.update_data(field="tag")
    elif callback.data == "edit_trailer":
        await callback.message.answer("🎬 Yangi treyler video yuboring:")
        await state.set_state(AnimeEdit.waiting_for_field)
        await state.update_data(field="trailer")
    elif callback.data == "edit_story":
        await callback.message.answer("📝 Yangi hikoyani kiriting:")
        await state.set_state(AnimeEdit.waiting_for_field)
        await state.update_data(field="story")
    elif callback.data == "delete_anime":
        database.delete_anime(anime_id)
        await callback.message.answer("❌ Anime o‘chirildi!")
        await state.clear()
    elif callback.data == "back_to_admin_panel":
        await callback.message.answer("👑 Admin panelga qaytish", reply_markup=admin_panel)
        await state.clear()

# ---------------- Yangi qiymatni saqlash ---------------- #
@router.message(AnimeEdit.waiting_for_field)
@admin_only
async def save_new_field(message: Message, state: FSMContext):
    data = await state.get_data()
    anime_id = data.get("anime_id")
    field = data.get("field")
    value = message.text

    database.update_anime_field(anime_id, field, value)
    await message.answer(f"✅ {field} yangilandi!")
    await state.clear()


    # ---------------- Sozlamalar ---------------- #


router = Router()

# ---------------- States ---------------- #
class BotSettings(StatesGroup):
    waiting_for_field = State()
    waiting_for_value = State()

# ---------------- Sozlamalar paneli ---------------- #
@router.message(F.text == "⚙️ Sozlamalar")
@admin_only
async def settings_panel(message: Message):
    settings = database.get_settings()
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"🤖 Bot ishlashi: {'✅' if settings['bot_active'] else '❌'}", callback_data="toggle_bot")],
        [InlineKeyboardButton(text=f"📢 Default kanal: {settings['default_channel']}", callback_data="edit_channel")],
        [InlineKeyboardButton(text=f"🔐 Majburiy obunalar: {'✅' if settings['mandatory_subs_enabled'] else '❌'}", callback_data="toggle_mandatory")],
        [InlineKeyboardButton(text=f"⏰ Avto post interval: {settings['auto_post_interval']} daqiqa", callback_data="edit_interval")],
        [InlineKeyboardButton(text=f"📊 Statistika: {'✅' if settings['stats_enabled'] else '❌'}", callback_data="toggle_stats")],
        [InlineKeyboardButton(text="◀️ Orqaga", callback_data="back_to_admin_panel")]
    ])
    
    await message.answer("⚙️ Bot sozlamalari:", reply_markup=kb)

# ---------------- Callback query handler ---------------- #
@router.callback_query()
@admin_only
async def settings_callbacks(callback: CallbackQuery, state: FSMContext):
    data = callback.data
    settings = database.get_settings()

    if data == "toggle_bot":
        database.update_setting('bot_active', 0 if settings['bot_active'] else 1)
        await callback.message.edit_text("✅ Bot ishlash holati o‘zgartirildi.")
        await settings_panel(callback.message)

    elif data == "edit_channel":
        await callback.message.answer("📢 Yangi default kanal username ni yuboring:")
        await state.update_data(field='default_channel')
        await state.set_state(BotSettings.waiting_for_value)

    elif data == "toggle_mandatory":
        database.update_setting('mandatory_subs_enabled', 0 if settings['mandatory_subs_enabled'] else 1)
        await callback.message.edit_text("✅ Majburiy obunalar holati o‘zgartirildi.")
        await settings_panel(callback.message)

    elif data == "edit_interval":
        await callback.message.answer("⏰ Yangi avtomatik post intervalini yuboring (daqiqalarda):")
        await state.update_data(field='auto_post_interval')
        await state.set_state(BotSettings.waiting_for_value)

    elif data == "toggle_stats":
        database.update_setting('stats_enabled', 0 if settings['stats_enabled'] else 1)
        await callback.message.edit_text("✅ Statistika monitoring holati o‘zgartirildi.")
        await settings_panel(callback.message)

    elif data == "back_to_admin_panel":
        await callback.message.answer("👑 Admin panelga qaytish", reply_markup=admin_panel)

# ---------------- Sozlamani saqlash ---------------- #
@router.message(BotSettings.waiting_for_value)
@admin_only
async def save_setting_value(message: Message, state: FSMContext):
    data = await state.get_data()
    field = data.get('field')

    if field == 'default_channel':
        if not message.text.startswith("@"):
            await message.answer("❌ Username noto‘g‘ri. @ bilan boshlanishi kerak.")
            return
        database.update_setting('default_channel', message.text)

    elif field == 'auto_post_interval':
        try:
            val = int(message.text)
            database.update_setting('auto_post_interval', val)
        except:
            await message.answer("❌ Iltimos, to‘g‘ri raqam kiriting!")
            return

    await message.answer("✅ Sozlama saqlandi!")
    await state.clear()



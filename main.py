import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from config import Config
from models.user import User, Tenant, CustomCommand
from utils.database import get_db, Base, engine
from sqlalchemy.orm import Session
import json
import requests
from datetime import datetime

# Buat tabel database
Base.metadata.create_all(bind=engine)

# Inisialisasi bot
bot = telebot.TeleBot(Config.BOT_TOKEN)

# Fungsi untuk mendapatkan prefix berdasarkan user
def get_user_prefix(user_id):
    db: Session = next(get_db())
    user = db.query(User).filter(User.user_id == user_id).first()
    if user and user.tenant:
        return user.tenant.prefix
    return Config.DEFAULT_PREFIX

# Middleware untuk menangani user
@bot.middleware_handler(update_types=['message'])
def register_user(bot_instance, message):
    db: Session = next(get_db())
    user_id = message.from_user.id
    user = db.query(User).filter(User.user_id == user_id).first()
    
    if not user:
        user = User(
            user_id=user_id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name
        )
        db.add(user)
        db.commit()

# Handler perintah start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    prefix = get_user_prefix(message.from_user.id)
    welcome_text = f"""
👋 Halo {message.from_user.first_name}! Saya adalah T.AI, chatbot multifungsi.

Saya dapat membantu Anda dengan berbagai kebutuhan:
📊 Informasi: cuaca, berita, jadwal sholat, dll.
⚡ Produktivitas: reminder, catatan, to-do list, dll.
🎮 Hiburan: tebak-tebakan, game, jokes, dll.
🤖 Teknologi & AI: chat AI, generate teks/gambar, dll.
👨‍💼 Admin: manajemen user, broadcast, dll.
💰 Ekonomi: cek kurs, crypto, emas, dll.

Gunakan {prefix}help untuk melihat semua perintah yang tersedia.
    """
    bot.reply_to(message, welcome_text)

# Handler perintah help
@bot.message_handler(commands=['help'])
def send_help(message):
    prefix = get_user_prefix(message.from_user.id)
    help_text = f"""
📋 **Daftar Perintah T.AI**

📊 **INFORMASI**
{prefix}cuaca [kota] - Dapatkan informasi cuaca
{prefix}berita [topik] - Dapatkan berita terbaru
{prefix}jadwal_sholat [kota] - Jadwal sholat
{prefix}kalender - Kalender dan tanggal penting
{prefix}translate [bahasa] [teks] - Terjemahkan teks
{prefix}kamus [kata] - Cari arti kata

⚡ **PRODUKTIVITAS**
{prefix}reminder [waktu] [pesan] - Set pengingat
{prefix}catatan [tambah/lihat/hapus] - Kelola catatan
{prefix}todo [tambah/lihat/hapus] - Kelola to-do list
{prefix}timer [waktu] - Set timer
{prefix}kalkulator [ekspresi] - Kalkulator
{prefix}konversi [nilai] [dari] [ke] - Konversi satuan

🎮 **HIBURAN**
{prefix}tebakgambar - Game tebak gambar
{prefix}tebakkata - Game tebak kata
{prefix}joke - Dapatkan joke lucu
{prefix}quote - Dapatkan quote inspiratif
{prefix}meme [teks] - Generate meme

🤖 **TEKNOLOGI & AI**
{prefix}ai [pertanyaan] - Chat dengan AI
{prefix}generate [prompt] - Generate teks
{prefix}generate_image [prompt] - Generate gambar
{prefix}ringkas [url] - Ringkas artikel

👨‍💼 **ADMIN** (Hanya untuk admin)
{prefix}broadcast [pesan] - Broadcast pesan
{prefix}users - Lihat jumlah user
{prefix}ban [user_id] - Ban user
{prefix}kick [user_id] - Kick user
{prefix}addcommand [nama] [response] - Tambah perintah custom

💰 **EKONOMI**
{prefix}kurs - Kurs mata uang
{prefix}crypto [coin] - Harga cryptocurrency
{prefix}emas - Harga emas
{prefix}ongkir [origin] [dest] [berat] - Hitung ongkir

🔧 **LAINNYA**
{prefix}profile - Lihat profil Anda
{prefix}settings - Pengaturan bot
{prefix}feedback [pesan] - Kirim feedback
    """
    bot.reply_to(message, help_text)

# Handler untuk perintah informasi
@bot.message_handler(commands=['cuaca'])
def handle_cuaca(message):
    if len(message.text.split()) < 2:
        bot.reply_to(message, "❌ Format: /cuaca [kota]")
        return
    
    kota = ' '.join(message.text.split()[1:])
    # Simulasi data cuaca
    cuaca_data = f"🌤️ Cuaca di {kota}: Cerah berawan\n🌡️ Suhu: 28°C\n💧 Kelembaban: 65%\n💨 Angin: 10 km/jam"
    bot.reply_to(message, cuaca_data)

@bot.message_handler(commands=['berita'])
def handle_berita(message):
    topik = 'terkini'
    if len(message.text.split()) > 1:
        topik = ' '.join(message.text.split()[1:])
    
    # Simulasi berita
    berita = f"📰 Berita {topik}:\n\n1. Indonesia raih emas di Olimpiade 2024\n2. Harga BBM turun mulai minggu depan\n3. Teknologi AI semakin canggih di tahun 2024"
    bot.reply_to(message, berita)

# Handler untuk perintah produktivitas
@bot.message_handler(commands=['kalkulator'])
def handle_kalkulator(message):
    if len(message.text.split()) < 2:
        bot.reply_to(message, "❌ Format: /kalkulator [ekspresi]")
        return
    
    try:
        ekspresi = ' '.join(message.text.split()[1:])
        # Hati-hati dengan eval, dalam produksi gunakan parser yang lebih aman
        hasil = eval(ekspresi)
        bot.reply_to(message, f"🧮 Hasil: {hasil}")
    except:
        bot.reply_to(message, "❌ Ekspresi matematika tidak valid")

@bot.message_handler(commands=['timer'])
def handle_timer(message):
    if len(message.text.split()) < 2:
        bot.reply_to(message, "❌ Format: /timer [waktu dalam detik]")
        return
    
    try:
        detik = int(message.text.split()[1])
        bot.reply_to(message, f"⏰ Timer diatur untuk {detik} detik")
        # Di sini bisa ditambahkan logika timer yang sesungguhnya
    except:
        bot.reply_to(message, "❌ Waktu harus angka")

# Handler untuk perintah hiburan
@bot.message_handler(commands=['joke'])
def handle_joke(message):
    jokes = [
        "Kenapa programmer tidak bisa tidur? Karena ada bug di kasurnya!",
        "Apa bedanya programmer dan politikus? Programmer hanya buat janji di kode, politikus beneran janji tapi gak ditepati!",
        "Kenapa komputer jarang sakit? Karena punya Windows!",
        "Apa bahasa programming favorit ular? Py-thon!"
    ]
    import random
    joke = random.choice(jokes)
    bot.reply_to(message, f"😂 {joke}")

@bot.message_handler(commands=['quote'])
def handle_quote(message):
    quotes = [
        "The only way to do great work is to love what you do. - Steve Jobs",
        "Innovation distinguishes between a leader and a follower. - Steve Jobs",
        "Your time is limited, so don't waste it living someone else's life. - Steve Jobs",
        "The future belongs to those who believe in the beauty of their dreams. - Eleanor Roosevelt"
    ]
    import random
    quote = random.choice(quotes)
    bot.reply_to(message, f"💬 {quote}")

# Handler untuk perintah admin (hanya owner)
@bot.message_handler(commands=['broadcast'])
def handle_broadcast(message):
    if str(message.from_user.id) != Config.OWNER_ID:
        bot.reply_to(message, "❌ Anda tidak memiliki izin untuk menggunakan perintah ini.")
        return
    
    if len(message.text.split()) < 2:
        bot.reply_to(message, "❌ Format: /broadcast [pesan]")
        return
    
    broadcast_message = ' '.join(message.text.split()[1:])
    db: Session = next(get_db())
    users = db.query(User).all()
    
    success = 0
    failed = 0
    
    for user in users:
        try:
            bot.send_message(user.user_id, f"📢 **Broadcast dari Admin:**\n\n{broadcast_message}", parse_mode='Markdown')
            success += 1
        except:
            failed += 1
    
    bot.reply_to(message, f"✅ Broadcast selesai:\nBerhasil: {success}\nGagal: {failed}")

@bot.message_handler(commands=['users'])
def handle_users(message):
    if str(message.from_user.id) != Config.OWNER_ID:
        bot.reply_to(message, "❌ Anda tidak memiliki izin untuk menggunakan perintah ini.")
        return
    
    db: Session = next(get_db())
    user_count = db.query(User).count()
    bot.reply_to(message, f"👥 Total pengguna: {user_count}")

# Handler untuk perintah ekonomi
@bot.message_handler(commands=['kurs'])
def handle_kurs(message):
    # Simulasi data kurs
    kurs_data = """
💱 Kurs Mata Uang (USD):
💰 IDR: 15,500
💶 EUR: 0.92
💷 GBP: 0.79
💴 JPY: 147.25
💵 CNY: 7.18
    """
    bot.reply_to(message, kurs_data)

@bot.message_handler(commands=['crypto'])
def handle_crypto(message):
    coin = 'bitcoin'
    if len(message.text.split()) > 1:
        coin = message.text.split()[1].lower()
    
    # Simulasi harga crypto
    prices = {
        'bitcoin': '$42,500',
        'ethereum': '$2,300',
        'bnb': '$310',
        'solana': '$95',
        'xrp': '$0.62'
    }
    
    if coin in prices:
        bot.reply_to(message, f"₿ Harga {coin}: {prices[coin]}")
    else:
        bot.reply_to(message, f"❌ Data untuk {coin} tidak ditemukan")

# Handler untuk perintah custom
@bot.message_handler(func=lambda message: True)
def handle_custom_commands(message):
    db: Session = next(get_db())
    user_id = message.from_user.id
    user = db.query(User).filter(User.user_id == user_id).first()
    
    if user and user.tenant:
        # Cek perintah custom
        text = message.text.lower()
        custom_command = db.query(CustomCommand).filter(
            CustomCommand.tenant_id == user.tenant_id,
            CustomCommand.command == text.split()[0].replace(user.tenant.prefix, '')
        ).first()
        
        if custom_command:
            bot.reply_to(message, custom_command.response)
            return
    
    # Jika bukan perintah custom, tangani dengan handler default
    if message.text.startswith('/'):
        bot.reply_to(message, "❌ Perintah tidak dikenali. Gunakan /help untuk melihat daftar perintah.")

# Jalankan bot
if __name__ == '__main__':
    print("Bot T.AI sedang berjalan...")
    bot.infinity_polling()

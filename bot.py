import telebot
from telebot import apihelper
from telebot.types import (ReplyKeyboardMarkup, KeyboardButton, 
                          InlineKeyboardMarkup, InlineKeyboardButton,
                          InputMediaPhoto, InputMediaVideo)
import requests
import json
import sqlite3
import datetime
import random
import time
import threading
import os
import re
import base64
import io
from PIL import Image, ImageDraw, ImageFont
from http.server import HTTPServer, BaseHTTPRequestHandler
import openai
import google.generativeai as genai
from urllib.parse import quote

# ========== KONFIGURASI ==========
apihelper.ENABLE_MIDDLEWARE = True

# API Keys
OPENAI_API_KEY = "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"
WEATHER_API_KEY = "4cd7ee1c-84af-11f0-b07a-0242ac130006-4cd7eee4-84af-11f0-b07a-0242ac130006"
NEWS_API_KEY = "Kr0x8kAMrOXKfOcTamdln7KtGkiE6PVaqX2sq7RK"
GEMINI_API_KEY = "AIzaSyCyCk_LjBxAYu1IVaN8FMdu_V1r0jh_Nvc"
MUSIC_API_KEY = "f9155ba279382388e928ba13989c914a"

# Inisialisasi API
openai.api_key = OPENAI_API_KEY
genai.configure(api_key=GEMINI_API_KEY)

# Owner information
OWNER_USERNAME = "@XyraaEx"
OWNER_ID = "083821223529"

# Inisialisasi bot
BOT_TOKEN = "8448925049:AAHDvpfxVj2muJvWDsSFRcjN8Dk1HqoivuQ"
bot = telebot.TeleBot(BOT_TOKEN)

# Database setup
def init_db():
    conn = sqlite3.connect('tai_bot.db')
    c = conn.cursor()
    
    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (user_id INTEGER PRIMARY KEY, username TEXT, first_name TEXT, 
                 last_name TEXT, is_premium INTEGER, premium_until TEXT, 
                 created_at TEXT, coins INTEGER)''')
    
    # Commands usage table
    c.execute('''CREATE TABLE IF NOT EXISTS commands_usage
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, 
                 command TEXT, used_at TEXT)''')
    
    # Games table
    c.execute('''CREATE TABLE IF NOT EXISTS games
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER,
                 game_type TEXT, score INTEGER, played_at TEXT)''')
    
    # Notes table
    c.execute('''CREATE TABLE IF NOT EXISTS notes
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER,
                 title TEXT, content TEXT, created_at TEXT)''')
    
    # Todos table
    c.execute('''CREATE TABLE IF NOT EXISTS todos
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER,
                 task TEXT, is_completed INTEGER, created_at TEXT)''')
    
    conn.commit()
    conn.close()

init_db()

# ========== UTILITY FUNCTIONS ==========
def get_user_info(user_id):
    conn = sqlite3.connect('tai_bot.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    user = c.fetchone()
    conn.close()
    return user

def create_user(user_id, username, first_name, last_name):
    conn = sqlite3.connect('tai_bot.db')
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users (user_id, username, first_name, last_name, is_premium, coins, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
              (user_id, username, first_name, last_name, 0, 100, datetime.datetime.now().isoformat()))
    conn.commit()
    conn.close()

def is_premium(user_id):
    user = get_user_info(user_id)
    if user and user[4] == 1:  # is_premium column
        premium_until = datetime.datetime.fromisoformat(user[5])
        return premium_until > datetime.datetime.now()
    return False

def is_owner(user_id):
    return str(user_id) == OWNER_ID

def log_command(user_id, command):
    conn = sqlite3.connect('tai_bot.db')
    c = conn.cursor()
    c.execute("INSERT INTO commands_usage (user_id, command, used_at) VALUES (?, ?, ?)",
              (user_id, command, datetime.datetime.now().isoformat()))
    conn.commit()
    conn.close()

def get_user_stats(user_id):
    conn = sqlite3.connect('tai_bot.db')
    c = conn.cursor()
    
    # Total commands used
    c.execute("SELECT COUNT(*) FROM commands_usage WHERE user_id=?", (user_id,))
    total_commands = c.fetchone()[0]
    
    # Most used command
    c.execute("SELECT command, COUNT(*) as count FROM commands_usage WHERE user_id=? GROUP BY command ORDER BY count DESC LIMIT 1", (user_id,))
    most_used = c.fetchone()
    
    conn.close()
    return total_commands, most_used

# ========== MIDDLEWARE ==========
@bot.middleware_handler(update_types=['message'])
def register_user(bot_instance, message):
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name or ""
    
    create_user(user_id, username, first_name, last_name)
    log_command(user_id, message.text.split()[0] if message.text else "unknown")

# ========== HEALTH CHECK SERVER ==========
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok", "message": "T.AI Bot is running"}).encode())
        else:
            self.send_response(404)
            self.end_headers()

def run_health_server():
    server = HTTPServer(('0.0.0.0', 8080), HealthHandler)
    print("Health check server running on port 8080")
    server.serve_forever()

health_thread = threading.Thread(target=run_health_server)
health_thread.daemon = True
health_thread.start()

# ========== 200+ PERINTAH BOT ==========

# === PERINTAH UMUM ===
@bot.message_handler(commands=['start'])
def start_command(message):
    user = message.from_user
    welcome_text = f"""
👋 Halo {user.first_name}! Saya adalah Tohang.AI, chatbot multifungsi dengan 200+ perintah.

✨Fitur Unggulan:
• AI Chat & Generate Konten
• Downloader Media Sosial
• Game Seru & RPG
• Tools Produktivitas
• Informasi Real-time
• Dan masih banyak lagi!

Gunakan /help untuk melihat semua perintah.
Gunakan /premium untuk upgrade ke premium.
    """
    bot.reply_to(message, welcome_text)

@bot.message_handler(commands=['help'])
def help_command(message):
    help_text = """
📋 KATEGORI PERINTAH Tohang.AI:

🤖AI & GENERATE
/ai [pertanyaan] - Chat dengan AI
/img [prompt] - Generate gambar
/video [prompt] - Generate video pendek
/music [genre] - Generate musik
/summarize [teks] - Ringkas teks
/translate [bahasa] [teks] - Terjemahkan

📥DOWNLOADER
/ytmp3 [url] - Download YouTube sebagai MP3
/ytmp4 [url] - Download YouTube sebagai MP4
/tiktok [url] - Download video TikTok
/instagram [url] - Download video/photo IG
/twitter [url] - Download video Twitter
/facebook [url] - Download video Facebook

🎮GAMES & RPG
/games - Lihat semua game
/rpg - Game RPG adventure
/quiz - Kuis pengetahuan
/trivia - Trivia seru
/guess - Tebak gambar
/wordgame - Game kata
/cards - Game kartu
/casino - Casino games
/slot - Mesin slot
/blackjack - Blackjack
/poker - Poker game
/race - Balapan
/adventure - Petualangan
/puzzle - Puzzle game
/memory - Game memori
/ticTacToe - Tic Tac Toe
/hangman - Hangman
/sudoku - Sudoku
/crossword - Crossword
/chess - Catur
/checkers - Checkers
/bingo - Bingo
/battle - Battle game
/arcade - Arcade games
/maze - Labirin
/jigsaw - Puzzle jigsaw
/rpg2 - RPG lanjutan
/rpg3 - RPG epic

💰EKONOMI & KRIPTO
/crypto [coin] - Harga cryptocurrency
/btc - Harga Bitcoin
/eth - Harga Ethereum
/stock [symbol] - Harga saham
/gold - Harga emas
/silver - Harga perak
/currency [from] [to] - Konversi mata uang
/portfolio - Kelola portfolio

🌤️INFORMASI & BERITA
/weather [kota] - Info cuaca
/news [topik] - Berita terbaru
/calendar - Kalender & event
/horoscope [zodiak] - Ramalan zodiak
/jadwalsholat [kota] - Jadwal sholat
/quotes - Quotes inspiratif
/facts - Fakta menarik
/jokes - Joke lucu
/trivia - Fakta trivia

⚡PRODUKTIVITAS
/notes - Kelola catatan
/todo - To-do list
/reminder [waktu] [pesan] - Set pengingat
/timer [waktu] - Timer
/calculator [ekspresi] - Kalkulator
/convert [nilai] [dari] [ke] - Konversi satuan
/QR [teks] - Generate QR code
/scanqr - Scan QR code

🎵MUSIK & AUDIO
/play [lagu] - Putar musik
/lyrics [lagu] - Lirik lagu
/radio [stasiun] - Dengarkan radio
/podcast [topik] - Podcast

📷FOTO & VIDEO
/editfoto [effect] - Edit foto
/filter [filter] - Filter foto
/collage - Buat collage
/meme [teks] - Buat meme
/gif [query] - Cari GIF

🔧UTILITIES
/qr [teks] - Generate QR
/barcode [teks] - Generate barcode
/color [hex] - Info warna
/font [teks] [font] - Ubah font
/encode [teks] - Encode teks
/decode [teks] - Decode teks
/password [panjang] - Generate password
/username [nama] - Generate username

👨‍💼PREMIUM & OWNER
/premium - Upgrade ke premium
/myprofile - Profile saya
/mystats - Statistik penggunaan
/transfer [user] [amount] - Transfer koin
/buy [item] - Beli item
/market - Market item

🔐OWNER ONLY (Hanya untuk owner)
/broadcast [pesan] - Broadcast ke semua user
/users - Total users
/stats - Statistik bot
/addpremium [user] - Tambah premium
/removepremium [user] - Hapus premium
/coins [user] [amount] - Tambah koin
/restart - Restart bot
/backup - Backup data

📚EDUCATION
/wiki [query] - Wikipedia search
/define [kata] - Definisi kata
/synonym [kata] - Sinonim
/antonym [kata] - Antonim
/translate [bahasa] [teks] - Terjemahan
/math [problem] - Bantuan matematika
/science [topic] - Sains
/history [event] - Sejarah
/grammar [teks] - Cek grammar

🎉FUN & ENTERTAINMENT
/fortune - Ramalan keberuntungan
/compliment - Pujian
/roast - Roast lucu
/8ball [pertanyaan] - Magic 8 ball
/dice - Lempar dadu
/coinflip - Lempar koin
/countdown [waktu] - Hitung mundur
/compatibility [nama1] [nama2] - Kecocokan

🛒E-COMMERCE
/shop - Lihat shop
/order [item] - Pesan item
/track [order_id] - Lacak pesanan
/coupon [kode] - Gunakan kupon
/cart - Keranjang belanja

📊DATA & ANALYTICS
/analyze [data] - Analisis data
/chart [data] - Buat chart
/plot [data] - Buat plot
/stats [data] - Statistik data

🌐WEB & TECH
/ip [ip] - Info IP address
/whois [domain] - Info domain
/ping [host] - Ping host
/website [url] - Info website
/speedtest - Test kecepatan internet

📅TIME & DATE
/time [zona] - Waktu sekarang
/date - Tanggal sekarang
/timer [waktu] - Set timer
/countdown [waktu] - Hitung mundur
/age [tanggal_lahir] - Hitung umur

🗺️MAPS & LOCATION
/map [tempat] - Peta lokasi
/navigation [dari] [ke] - Navigasi
/places [query] - Tempat terdekat

🧠PSIKOLOGI & KESEHATAN
/mood - Cek mood
/stress - Test stres
/health [tips] - Tips kesehatan
/meditate [waktu] - Meditasi
/sleep - Tips tidur

📱SOCIAL MEDIA
/tweet [teks] - Generate tweet
/instagram [teks] - Generate post IG
/facebook [teks] - Generate post FB
/story [teks] - Generate story

🎨ART & DESIGN
/art [style] [prompt] - Generate art
/design [template] - Template design
/logo [nama] - Generate logo
/palette - Color palette

⚙️SETTINGS
/settings - Pengaturan bot
/language [bahasa] - Ubah bahasa
/notifications - Set notifikasi
/privacy - Pengaturan privasi

📖STORIES & CONTENT
/story [genre] - Generate cerita
/poem [tema] - Generate puisi
/joke [kategori] - Joke berdasarkan kategori
/quote [kategori] - Quote berdasarkan kategori

🔍SEARCH TOOLS
/search [query] - Search internet
/images [query] - Cari gambar
/videos [query] - Cari video
/news [query] - Cari berita

📂FILE TOOLS
/compress [file] - Kompres file
/convertfile [format] - Konversi file
/edit [file] - Edit file

🎯PERSONALIZATION
/profile - Profile pengguna
/achievements - Pencapaian
/badges - Lencana
/level - Level pengguna

🤝SOCIAL FEATURES
/friends - Daftar teman
/leaderboard - Peringkat pengguna
/chat [user] - Chat dengan user
/group - Buat grup

🔔NOTIFICATIONS
/notify [pesan] - Notifikasi
/alerts - Set alerts
/reminders - Daftar reminder

📈FINANCIAL TOOLS
/budget - Kelola budget
/expenses - Catat pengeluaran
/investment - Kalkulator investasi
/loan - Kalkulator pinjaman

🧩 MINI TOOLS
/roll [dice] - Lempar dadu
/choose [pilihan1, pilihan2] - Pilih acak
/counter - Penghitung
/random [min] [max] - Angka random

🛠️ **DEVELOPER TOOLS**
/code [bahasa] [kode] - Run code
/json [data] - Format JSON
/xml [data] - Format XML
/api [endpoint] - Test API

🎁 **SPECIAL FEATURES**
/daily - Hadiah harian
/rewards - Klaim hadiah
/spin - Spin wheel
/lottery - Lotere

Gunakan /premium untuk mengakses fitur premium!
    """
    bot.reply_to(message, help_text)

# === PREMIUM & OWNER COMMANDS ===
@bot.message_handler(commands=['premium'])
def premium_command(message):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("💎 Upgrade Premium", callback_data="buy_premium"))
    keyboard.add(InlineKeyboardButton("ℹ️ Info Premium", callback_data="premium_info"))
    
    premium_text = """
💎 PREMIUM MEMBERSHIP

Nikmati fitur eksklusif dengan upgrade ke premium:

✨ Fitur Premium:
• Akses semua 200+ perintah
• Generate gambar & video tanpa batas
• Downloader semua platform
• Game premium tanpa ads
• Priority support
• Bonus koin harian

💰 Harga:
• 1 Bulan: Rp 25.000
• 3 Bulan: Rp 60.000 (hemat 20%)
• 1 Tahun: Rp 200.000 (hemat 33%)

Klik tombol di bawah untuk upgrade!
    """
    bot.reply_to(message, premium_text, reply_markup=keyboard)

@bot.message_handler(commands=['myprofile'])
def myprofile_command(message):
    user_id = message.from_user.id
    user = get_user_info(user_id)
    
    if user:
        premium_status = "✅ Premium" if is_premium(user_id) else "❌ Regular"
        premium_until = user[5] if user[5] else "Tidak aktif"
        coins = user[7] if user[7] else 0
        
        profile_text = f"""
👤 PROFILE USER

🆔 ID: {user_id}
👤 Name: {user[2]} {user[3]}
📛 Username: @{user[1] if user[1] else 'N/A'}
💎 Status: {premium_status}
💰 Coins: {coins}
📅 Premium until: {premium_until}
📊 Joined: {user[6]}
        """
        bot.reply_to(message, profile_text)
    else:
        bot.reply_to(message, "❌ User tidak ditemukan.")

# === AI & GENERATE COMMANDS ===
@bot.message_handler(commands=['ai'])
def ai_chat_command(message):
    if len(message.text.split()) < 2:
        bot.reply_to(message, "❌ Format: /ai [pertanyaan]")
        return
    
    prompt = ' '.join(message.text.split()[1:])
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500
        )
        bot.reply_to(message, f"🤖 AI Response:\n\n{response.choices[0].message.content}")
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

@bot.message_handler(commands=['img'])
def generate_image_command(message):
    if not is_premium(message.from_user.id):
        bot.reply_to(message, "❌ Fitur ini hanya untuk user premium. Gunakan /premium untuk upgrade.")
        return
    
    if len(message.text.split()) < 2:
        bot.reply_to(message, "❌ Format: /img [prompt]")
        return
    
    prompt = ' '.join(message.text.split()[1:])
    
    try:
        response = openai.Image.create(
            prompt=prompt,
            n=1,
            size="1024x1024"
        )
        image_url = response['data'][0]['url']
        bot.send_photo(message.chat.id, image_url, caption=f"🖼️ Generated image for: {prompt}")
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

@bot.message_handler(commands=['music'])
def generate_music_command(message):
    if not is_premium(message.from_user.id):
        bot.reply_to(message, "❌ Fitur ini hanya untuk user premium. Gunakan /premium untuk upgrade.")
        return
    
    genre = "pop" if len(message.text.split()) < 2 else message.text.split()[1]
    
    try:
        # Simulate music generation
        music_info = f"""
🎵 Generated {genre} music track:

Title: {genre.title()} Melody
Duration: 3:45
BPM: 120
Key: C Major

🔊 Music is being generated... (simulation)
        """
        bot.reply_to(message, music_info)
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

# === DOWNLOADER COMMANDS ===
@bot.message_handler(commands=['ytmp3'])
def youtube_mp3_command(message):
    if len(message.text.split()) < 2:
        bot.reply_to(message, "❌ Format: /ytmp3 [youtube_url]")
        return
    
    url = message.text.split()[1]
    bot.reply_to(message, f"📥 Downloading MP3 from: {url}\n\n⏳ Please wait...")

@bot.message_handler(commands=['tiktok'])
def tiktok_download_command(message):
    if len(message.text.split()) < 2:
        bot.reply_to(message, "❌ Format: /tiktok [tiktok_url]")
        return
    
    url = message.text.split()[1]
    bot.reply_to(message, f"📥 Downloading TikTok video from: {url}\n\n⏳ Please wait...")

# === GAME COMMANDS ===
@bot.message_handler(commands=['games'])
def games_command(message):
    games_text = """
🎮 AVAILABLE GAMES

1. /rpg - RPG Adventure Game
2. /quiz - Knowledge Quiz
3. /trivia - Trivia Game
4. /guess - Guess the Image
5. /wordgame - Word Game
6. /cards - Card Games
7. /casino - Casino Games
8. /slot - Slot Machine
9. /blackjack - Blackjack
10. /poker - Poker Game
11. /race - Racing Game
12. /adventure - Adventure Game
13. /puzzle - Puzzle Game
14. /memory - Memory Game
15. /ticTacToe - Tic Tac Toe
16. /hangman - Hangman
17. /sudoku - Sudoku
18. /crossword - Crossword
19. /chess - Chess
20. /checkers - Checkers
21. /bingo - Bingo
22. /battle - Battle Game
23. /arcade - Arcade Games
24. /maze - Maze Game
25. /jigsaw - Jigsaw Puzzle
26. /rpg2 - Advanced RPG
27. /rpg3 - Epic RPG

🎯 Use any command to start playing!
    """
    bot.reply_to(message, games_text)

@bot.message_handler(commands=['rpg'])
def rpg_game_command(message):
    game_text = """
🎮 RPG ADVENTURE

You are a brave warrior in the kingdom of Eldoria.

Choose your action:
/attack - Attack the enemy
/defend - Defend yourself
/magic - Use magic
/run - Run away
/inventory - Check inventory
/stats - Check your stats

Your journey begins now! 🌟
    """
    bot.reply_to(message, game_text)

# === WEATHER & NEWS COMMANDS ===
@bot.message_handler(commands=['weather'])
def weather_command(message):
    if len(message.text.split()) < 2:
        bot.reply_to(message, "❌ Format: /weather [city]")
        return
    
    city = ' '.join(message.text.split()[1:])
    
    try:
        # Simulate weather API call
        weather_data = f"""
🌤️ Weather in {city.title()}

🌡️ Temperature: 28°C
💧 Humidity: 65%
☁️ Condition: Partly Cloudy
💨 Wind: 10 km/h
🌅 Sunrise: 05:45 AM
🌇 Sunset: 06:30 PM

📍 Location: {city.title()}
        """
        bot.reply_to(message, weather_data)
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

@bot.message_handler(commands=['news'])
def news_command(message):
    topic = "general" if len(message.text.split()) < 2 else message.text.split()[1]
    
    try:
        # Simulate news API call
        news_data = f"""
📰Latest News about {topic.title()} 

1. Breaking News: Major development in {topic} industry
2. Technology Advancements: New innovations in {topic} field
3. Market Update: Latest trends and analysis
4. Expert Opinions: Insights from industry leaders

Stay informed with the latest updates!
        """
        bot.reply_to(message, news_data)
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

# === PRODUCTIVITY COMMANDS ===
@bot.message_handler(commands=['notes'])
def notes_command(message):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("➕ Add Note", callback_data="add_note"))
    keyboard.add(InlineKeyboardButton("📋 View Notes", callback_data="view_notes"))
    
    notes_text = """
📝 NOTES MANAGER

Manage your personal notes with ease:

• Create unlimited notes
• Organize by categories
• Set reminders for note

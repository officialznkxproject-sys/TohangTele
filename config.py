import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Token bot dari @BotFather
    BOT_TOKEN = os.getenv('BOT_TOKEN', '8448925049:AAHDvpfxVj2muJvWDsSFRcjN8Dk1HqoivuQ')
    
    # Konfigurasi owner
    OWNER_ID = os.getenv('OWNER_ID', '083131871328')
    
    # Konfigurasi database
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///tai.db')
    
    # Konfigurasi API eksternal
    OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY', '')
    NEWS_API_KEY = os.getenv('NEWS_API_KEY', '')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    
    # Prefix default
    DEFAULT_PREFIX = os.getenv('DEFAULT_PREFIX', '/')

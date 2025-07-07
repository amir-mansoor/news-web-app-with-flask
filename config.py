import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'super-secret-key'  # 🔒 Change this in production
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'app/static/uploads')
    DATABASE = os.path.join(BASE_DIR, 'instance', 'news.db')
import os

class Config:
    # Flask 애플리케이션 설정
    DEBUG = True
    SECRET_KEY = 'your-secret-key'
    
    # 캐시 설정
    CACHE_TYPE = 'filesystem'
    CACHE_DIR = 'cache'
    CACHE_DEFAULT_TIMEOUT = 300

    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    STATIC_FOLDER = os.path.join(BASE_DIR, 'static')
    TEMPLATE_FOLDER = os.path.join(BASE_DIR, 'templates')
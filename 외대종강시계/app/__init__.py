from flask import Flask
import os
from config import Config

app = Flask(__name__,
           static_folder=Config.STATIC_FOLDER,
           template_folder=Config.TEMPLATE_FOLDER)

# CSS 파일 존재 여부 확인
css_files = [
    'css/main.css',
    'css/components/current-time.css',
    'css/components/meal.css',
    'css/components/notice-board.css',
    'css/components/timer.css',
    'css/themes/layout.css',
    'css/themes/themes.css',
    'css/themes/transitions.css',
    'css/responsive.css'
]

print("\nChecking CSS files:")
for css_file in css_files:
    file_path = os.path.join(Config.STATIC_FOLDER, css_file)
    print(f"{css_file}: {'EXISTS' if os.path.exists(file_path) else 'MISSING'}")

# routes import should be after app initialization
from app import routes
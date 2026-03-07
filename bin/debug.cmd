@echo off
call venv\Scripts\activate
python venv\Lib\site-packages\debugpy --listen 0.0.0.0:5678 cataflask.py
pause

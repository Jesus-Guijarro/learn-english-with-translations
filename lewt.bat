@echo off

cd /d "%~dp0"

REM call lewtvenv\Scripts\activate #Para activar el entorno lewtvenv

start "" python run.py

start "" "http://127.0.0.1:5000/"
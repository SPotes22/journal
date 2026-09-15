#!/bin/bash
echo "🕸️ Desplegando my_app..."
pip install -r requirements.txt
flask --app app.py init-db
python app.py

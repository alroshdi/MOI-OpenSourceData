# -*- coding: utf-8 -*-
"""
Flask WSGI entry for Vercel (Flask preset expects main.py at repository root).
Local dev: python dashboard_app.py → http://127.0.0.1:8050
"""
from dashboard_app import server as app

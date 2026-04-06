# -*- coding: utf-8 -*-
"""
Vercel Serverless Function — Flask WSGI (Dash). See api/ requirement for Python on Vercel.
Local: python dashboard_app.py → http://127.0.0.1:8050
"""
import os
import sys

_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _root not in sys.path:
    sys.path.insert(0, _root)

from dashboard_app import server as app

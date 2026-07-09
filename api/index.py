"""Ponto de entrada do Vercel (Python serverless).

O Vercel detecta a variável `app` como aplicação WSGI e a serve. Como o projeto
Django fica na subpasta `elo/` (onde está o manage.py), adicionamos essa pasta
ao sys.path antes de importar as settings.
"""

import os
import sys
from pathlib import Path

# .../ELO/api/index.py  ->  raiz do repo = parents[1]
BASE_DIR = Path(__file__).resolve().parents[1]
DJANGO_DIR = BASE_DIR / 'elo'

if str(DJANGO_DIR) not in sys.path:
    sys.path.insert(0, str(DJANGO_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'elo.settings')

from django.core.wsgi import get_wsgi_application  # noqa: E402

app = get_wsgi_application()

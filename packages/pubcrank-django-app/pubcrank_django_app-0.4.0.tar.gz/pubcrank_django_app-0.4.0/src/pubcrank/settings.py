import os
from pathlib import Path

from pubcrank.serialize import DateTimeSerializer

FIELD_SERIALIZERS = {
  'forms.DateTimeField': DateTimeSerializer
}

def setup_pubcrank(
    settings,
    pubdir=Path(os.environ.get('PUBCRANK_DIR', '.')),
    theme=os.environ.get('PUBCRANK_THEME')
  ):
  settings['PUBCRANK_DIR'] = pubdir
  settings['PUBCRANK_THEME'] = theme
  settings['TEMPLATES'].append({
    'NAME': 'pubcrank',
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [pubdir / 'themes'],
    'APP_DIRS': True,
    'OPTIONS': {
        'context_processors': [
            'django.template.context_processors.request',
            'django.contrib.auth.context_processors.auth',
            'django.contrib.messages.context_processors.messages',
        ],
    },
  })

  settings['PUBCRANK_MD_EXTRAS'] = ["fenced-code-blocks", "footnotes", "tables", "strike"]
  settings['PUBCRANK_FIELD_SERIALIZERS'] = FIELD_SERIALIZERS
  settings['PUBCRANK_PER_PAGE'] = 5

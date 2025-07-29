# PubCrank Django App

PubCrank is a static file CMS. `pubcrank-django-app` is a portable Django app that you can add to your Django project for static file CMS functionality.

**Note: this app is under construction**

## Installation and Setup

### Install

`pdm add pubcrank-django-app`

### settings.py

Add to `INSTALLED_APPS`

```python
INSTALLED_APPS = [
    ...
    'pubcrank',
]
```

Add PubCrank Settings:

```python
from pubcrank.settings import setup_pubcrank

# setup_pubcrank(globals(), pubcrank_dir_path, theme)
setup_pubcrank(globals(), BASE_DIR / 'pubdir', 'plain')
```

## Build Static Site

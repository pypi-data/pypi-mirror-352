from copy import copy
from pathlib import Path

from django.conf import settings
from django.core.paginator import Paginator

import frontmatter


def meta_sort_key(sortby):
  def sort_key(item):
    return item['metadata'][sortby]

  return sort_key


def file_sort_key(item):
  return item['file'].resolve().lower()


def load_pagination(context, listdir=".", recursive=True, sortby='-date'):
  if not isinstance(listdir, Path):
    if listdir.startswith('.'):
      listdir = context['src'].parent.joinpath(listdir)

    else:
      listdir = Path(listdir)

  to_process = []
  if recursive:
    for root, dirs, files in listdir.walk(on_error=context['crank'].no_access):
      for f in files:
        file = root / f
        if f.lower() != 'index.md' and file.suffix.lower() == '.md':
          metadata, content, template = context['crank'].open_content(file)
          to_process.append({'file': file, 'metadata': metadata})

  else:
    for file in listdir.iterdir():
      if file.name.lower() != 'index.md' and file.is_file() and file.suffix.lower() == '.md':
        metadata, content = context['crank'].open_content(file)
        to_process.append({'file': file, 'metadata': metadata})

  reverse = False
  if sortby.startswith('-'):
    reverse = True
    sortby = sortby[1:]

  if sortby == 'filename':
    to_process = sorted(to_processs, key=file_sort_key)

  else:
    to_process = sorted(to_process, key=meta_sort_key(sortby))

  if reverse:
    to_process.reverse()

  return Paginator(to_process, settings.PUBCRANK_PER_PAGE)

from copy import deepcopy
from pathlib import Path
import shutil

from django.template import Context, Template, engines
from django.conf import settings

import frontmatter
import hjson
import markdown2
from rich.console import Console

from pubcrank.lib.frontmatter import HJSONHandler
from pubcrank.pagination import load_pagination

econsole = Console(stderr=True, style="bold red")
console = Console()


class Crank:
  @staticmethod
  def parse_config(config):
    with config.open('r') as fh:
      return hjson.loads(fh.read())

  def __init__(self, config, pubdir, baseurl, verbose=False):
    self.verbose = verbose
    self.baseurl = baseurl
    self.config = config

    self.dir = pubdir

    self.content_dir = self.dir / "content"
    self.templates_dir = self.dir / "templates"
    self.assets_dir = self.dir / "assets"

    self.theme_dir = self.dir / "themes" / self.config["theme"]
    self.theme_assets_dir = self.theme_dir / "assets"

    self.content_cache = {}
    self.tpl_cache = {}
    self.tpl_engine = None
    for e in engines.all():
      if e.name == 'pubcrank':
        self.tpl_engine = e.engine

  def no_access(self, error):
    econsole.print(f'Can not access: {error.filename}')

  def log(self, message):
    if self.verbose:
      console.print(message)

  def success(self, message):
    console.print(message, style="green")

  def clear(self, outdir):
    if self.verbose:
      self.log(f"Clearing: {outdir}")

    shutil.rmtree(outdir, ignore_errors=True)

  def copy_assets(self, srcdir, outdir):
    if srcdir.exists():
      outdir.mkdir(parents=True, exist_ok=True)
      if self.verbose:
        self.log(f"Copying Assets: {srcdir}")

      shutil.copytree(srcdir, outdir, symlinks=True, dirs_exist_ok=True)

  def build(self, outdir, noclear=False):
    if not noclear:
      self.clear(outdir)

    self.copy_assets(self.theme_assets_dir, outdir)
    self.copy_assets(self.assets_dir, outdir)

    for root, dirs, files in self.content_dir.walk(on_error=self.no_access):
      for f in files:
        file = root / f
        if file.suffix.lower() == '.md':
          relpath = file.relative_to(self.content_dir)
          outpath = outdir / relpath
          outpath = outpath.with_suffix('.html')
          self.generate(file, outpath)

    self.success(f"Successful build: {outdir.resolve()}")

  def get_template(self, tpl_file):
    if tpl_file not in self.tpl_cache:
      tpl_path = self.templates_dir / tpl_file
      if not tpl_path.exists():
        tpl_path = self.theme_dir / tpl_file

      with tpl_path.open('r') as fh:
        tpl = Template(fh.read(), engine=self.tpl_engine)

      meta_path = tpl_path.with_suffix('.hjson')
      metadata = {}
      if meta_path.exists():
        with meta_path.open('r') as fh:
          metadata = hjson.loads(fh.read())

      self.tpl_cache[tpl_file] = (tpl, metadata)

    return self.tpl_cache[tpl_file]

  def hydrate_metadata(self, meta, tmeta):
    for field in tmeta.get('fields', []):
      key = field['name']
      if key in meta and field['type'] in settings.PUBCRANK_FIELD_SERIALIZERS:
        meta[key] = settings.PUBCRANK_FIELD_SERIALIZERS[field['type']].from_json(meta[key])

  def open_content(self, file):
    key = file.resolve()
    if key in self.content_cache:
      return self.content_cache[key]

    with file.open('r') as fh:
      metadata, content = frontmatter.parse(fh.read(), handler=HJSONHandler())

    template, template_metadata = self.get_template(metadata.get('template', 'page.html'))
    self.hydrate_metadata(metadata, template_metadata)

    self.content_cache[key] = (metadata, content, template)
    return self.content_cache[key]

  def write_output(self, context, template):
    self.log(f"Writing: {context['src']} -> {context['dest']}")
    context = Context(context)
    html = template.render(context)

    context['dest'].parent.mkdir(parents=True, exist_ok=True)
    with context['dest'].open('w') as fh:
      fh.write(html)

  def generate(self, src, dest):
    metadata, content, template = self.open_content(src)

    context = deepcopy(self.config)
    context['baseurl'] = self.baseurl
    context['_crank'] = self
    context['src'] = src
    context['dest'] = dest
    context['crank'] = self

    page = metadata
    content = markdown2.markdown(content, extras=settings.PUBCRANK_MD_EXTRAS)
    page.update({'body': content})
    context.update({'page': page})

    if 'paginate' in metadata:
      paginator = load_pagination(context, **metadata['paginate'])

      for p in paginator.page_range:
        page = paginator.page(p)
        pdest = context['dest'].parent / 'page' / str(page.number) / 'index.html'
        pcontext = deepcopy(context)
        pcontext['dest'] = pdest
        pcontext['pagination'] = page
        self.write_output(pcontext, template)
        if p == 1:
          pdest = context['dest'].parent / 'index.html'
          pcontext['dest'] = pdest
          self.write_output(pcontext, template)

    else:
      self.write_output(context, template)

import hjson

from frontmatter.default_handlers import JSONHandler
from frontmatter.util import u


class HJSONHandler(JSONHandler):
  def load(self, fm, **kwargs):
    return hjson.loads(fm, **kwargs)

  def export(self, metadata, **kwargs):
    kwargs.setdefault("indent", 2)
    metadata_str = hjson.dumps(metadata, **kwargs)
    return u(metadata_str)

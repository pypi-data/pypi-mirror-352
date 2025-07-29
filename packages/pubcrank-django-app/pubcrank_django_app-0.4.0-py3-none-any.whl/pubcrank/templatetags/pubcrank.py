import re
from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def page_url(context, page_obj):
  relpath = page_obj['file'].relative_to(context['_crank'].content_dir)
  relpath = relpath.with_suffix('.html')
  relpath = re.sub("(/index.html)$", "/", str(relpath), flags=re.I)
  return context['baseurl'] + relpath

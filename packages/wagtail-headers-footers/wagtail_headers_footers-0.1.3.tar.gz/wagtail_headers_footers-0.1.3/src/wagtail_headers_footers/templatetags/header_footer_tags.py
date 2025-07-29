from django import template
from django.utils.safestring import mark_safe
from wagtail.models import Site

from wagtail_headers_footers.models import HeaderFooterScriptsSettings

register = template.Library()


@register.simple_tag(takes_context=True)
def render_header_scripts(context):
    request = context.get('request')
    page = context.get('page')
    site = Site.find_for_request(request)

    scripts = []

    settings = HeaderFooterScriptsSettings.for_site(site)

    # scripts += [
    #     f"<!-- Start {header.name} -->\n{header.content}\n<!-- End {header.name} -->"
    #     for header in settings.headers.all() if header.is_active
    # ]

    scripts += [h.content for h in settings.headers.all() if h.is_active]

    if hasattr(page, 'extra_headers'):
        scripts += [h.content for h in page.extra_headers.all() if h.is_active]

    return mark_safe('\n'.join(scripts))


@register.simple_tag(takes_context=True)
def render_footer_scripts(context):
    request = context.get('request')
    page = context.get('page')
    site = Site.find_for_request(request)

    scripts = []

    settings = HeaderFooterScriptsSettings.for_site(site)

    scripts += [f.content for f in settings.footers.all() if f.is_active]

    if hasattr(page, 'extra_footers'):
        scripts += [f.content for f in page.extra_footers.all() if f.is_active]

    return mark_safe('\n'.join(scripts))

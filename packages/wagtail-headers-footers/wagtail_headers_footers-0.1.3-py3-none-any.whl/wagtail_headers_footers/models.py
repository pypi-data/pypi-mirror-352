from django.db import models
from django.utils.translation import gettext_lazy as _
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.admin.widgets import SwitchInput
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting
from wagtail.models import Orderable


class BaseHeaderFooterScript(Orderable):
    """Abstract base model representing a header or footer script."""

    name = models.CharField(
        max_length=255,
        help_text=_('A short name to identify the script.'),
    )
    content = models.TextField(
        _('Content'),
        help_text=_('The raw script content to be injected into the site.'),
    )
    is_active = models.BooleanField(
        default=True,
        help_text=_('Whether the script should be included in the page output.'),
    )

    panels = [
        FieldPanel('name'),
        FieldPanel('content'),
        FieldPanel('is_active', widget=SwitchInput()),
    ]

    def __str__(self):
        return self.name


class HeaderScript(BaseHeaderFooterScript):
    """Script to be injected into the <head> of the site."""

    settings = ParentalKey(
        'HeaderFooterScriptsSettings',
        on_delete=models.CASCADE,
        related_name='headers',
    )


class FooterScript(BaseHeaderFooterScript):
    """Script to be injected before the closing </body> tag of the site."""

    settings = ParentalKey(
        'HeaderFooterScriptsSettings',
        on_delete=models.CASCADE,
        related_name='footers',
    )


class PageHeaderScript(BaseHeaderFooterScript):
    page = ParentalKey(
        'wagtailcore.Page',
        on_delete=models.CASCADE,
        related_name='extra_headers',
    )


class PageFooterScript(BaseHeaderFooterScript):
    page = ParentalKey(
        'wagtailcore.Page',
        on_delete=models.CASCADE,
        related_name='extra_footers',
    )


@register_setting(icon='code')
class HeaderFooterScriptsSettings(BaseSiteSetting, ClusterableModel):
    """A Wagtail site setting for managing scripts injected into <head> and before </body> of each page."""

    panels = [
        MultiFieldPanel(
            [
                InlinePanel(
                    'headers',
                    label=_(' '),
                    help_text=_('Add tracking scripts between the <head> tags.'),
                ),
            ],
            heading=_('Headers'),
        ),
        MultiFieldPanel(
            [
                InlinePanel(
                    'footers',
                    label=_(' '),
                    help_text=_('Add tracking scripts before closing </body> tag.'),
                ),
            ],
            heading=_('Footers'),
        ),
    ]

    class Meta:
        verbose_name = _('Headers & Footers')
        verbose_name_plural = _('Headers & Footers')


class PageHeaderFooterScriptsMixin(models.Model):
    """Mixin to include page-specific header and footer scripts."""

    class Meta:
        abstract = True

    header_footer_panels = [
        MultiFieldPanel(
            [
                InlinePanel(
                    'extra_headers',
                    label=_(' '),
                    help_text=_('Scripts to inject into the <head> for this page.'),
                ),
            ],
            heading=_('Headers'),
        ),
        MultiFieldPanel(
            [
                InlinePanel(
                    'extra_footers',
                    label=_(' '),
                    help_text=_('Scripts to inject before </body> for this page.'),
                ),
            ],
            heading=_('Footers'),
        ),
    ]

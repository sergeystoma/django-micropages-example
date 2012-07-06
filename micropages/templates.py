"""
Wrapper for loading templates from the database, allowing a small degree of version control and publishing.
"""

from django.conf import settings
from django.template import TemplateDoesNotExist
from django.template.loader import BaseLoader
from django.utils._os import safe_join

import logging, re

from micropages.models import Page

# URL pattern for micropages, captures any page URL and allows to add a version after the link.
# This is not the pattern that should be added to urls.py mapping, rather micropages expects to receieve the full URL,
# and perform parsing later. For example, urls.py could look like:
# urlpatterns = patterns('',
#    ...
#    url(r'^.*$', 'micropages.views.page')
# )
#
# For best results, should be added after all other specific URL patterns to allow overrides of CMS pages, or 
# allow admin to still function.
URL_PATTERN = r'^(?P<page>[^@]*)(?:@(?P<version>\d*))?$'
url_pattern_compiled = re.compile(URL_PATTERN)

class Loader(BaseLoader):
    """
    Loads pages and templates from database.
    """
    is_usable = True

    def find_page(self, page_name):
        """
        Tries to locate a page or a template based on information stored in requested page name. 
        """
        path, version = url_pattern_compiled.match(page_name).groups()

        try:
            if version == None:
                return Page.objects.filter(path__exact=path, published__exact=True).order_by('-version')[0:1].get()
            else:
                return Page.objects.filter(path__exact=path, version__exact=version)[0:1].get()
        except Page.DoesNotExist:
            raise TemplateDoesNotExist('Tried looking for {0}'.format(page_name))

    def load_template_source(self, template_name, template_dirs=None):
        return (self.find_page(template_name).content, template_name)
    load_template_source.is_usable = True

from micropages.models import Page
from django.contrib import admin
from django.template import defaultfilters, Template, RequestContext
from django.http import HttpResponse
from django.conf.urls.defaults import patterns, include, url

import string

class PageAdmin(admin.ModelAdmin):
    fields = ('path', 'published', 'version', 'branched_from', 'content')
    readonly_fields = ('branched_from', 'published', 'version')

    list_display = ('path', 'pretty_content', 'version', 'pretty_branched_from', 'published')
    list_filter = ('published', 'path')
    ordering = ('path', '-version')

    actions = ('create_version', 'publish_version')

    def pretty_content(self, model):
        """
        Returns a truncated version of template content.
        """
        return model.content[:100] + '...'
    pretty_content.short_description = 'Content'

    def pretty_branched_from(self, model):
        """
        Replaces (None) with an empty string when page is not derived from a previous version.
        """
        return model.branched_from or ''
    pretty_branched_from.short_description = 'Branched From'

    def create_version(self, request, queryset):        
        """
        Create new versions of selected pages.
        """
        for model in queryset:
            self.create_page_version(model)
        versions_created = len(queryset)
        self.message_user(request, '{0} version{1} created'.format(versions_created, defaultfilters.pluralize(versions_created)))
    create_version.short_description = 'Create a version'

    def create_page_version(self, model):
        """
        Creates a view of a single page.
        """
        model.copy_as_version().save()

    def publish_version(self, request, queryset):
        """
        Publishes selected versions, while un-publishing all other pages for selected paths.
        """
        paths = []
        for model in queryset:
            Page.objects.publish(model)
            paths.append(model.path)
        self.message_user(request, '{0} published'.format(string.join(list(set(paths)), ', ')))
    publish_version.short_description = 'Publish'

    def preview(self, request):
        """
        Generates a preview of a page being edited.
        """
        if request.method != 'POST':
            return HttpResponse(status=405)

        if not('page' in request.POST):
            return HttpResponse(status=500)

        t = Template(request.POST['page'])
        c = RequestContext(request)
        r = HttpResponse(t.render(c), mimetype='text/html')
        r['X-XSS-Protection'] = '0'
        return r

    def get_urls(self):
        """
        Adds custom views to the admin site.
        """
        urls = super(PageAdmin, self).get_urls()
        page_urls = patterns('',
                (r'^preview/$', self.admin_site.admin_view(self.preview))
            )
        return page_urls + urls


admin.site.register(Page, PageAdmin)

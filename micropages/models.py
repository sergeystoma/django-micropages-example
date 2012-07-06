from django.db import models
from django.db.models import Max

class PageManager(models.Manager):    
    def publish(self, page):
        Page.objects.filter(path__exact=page.path).update(published=False)
        page.published=True
        page.save()

class Page(models.Model):
    """
    Both a template and a page.
    """
    path = models.CharField(max_length=255)
    content = models.TextField(blank=True)
    version = models.IntegerField(default=1)
    branched_from = models.IntegerField(blank=True, null=True)
    published = models.BooleanField()
    modified = models.DateTimeField(auto_now=True, auto_now_add=True)
    objects = PageManager()
    
    def copy_as_version(self):
        next_version = Page.objects.filter(path__exact=self.path).aggregate(Max('version'))['version__max'] + 1
        return Page(path=self.path, content=self.content, version=next_version, branched_from=self.version, published=False)

    def __unicode__(self):
        return self.path


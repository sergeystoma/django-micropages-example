from django.http import HttpResponse, Http404
from django.template import RequestContext, Template
from django.template import TemplateDoesNotExist

import templates

def page(request):
    try:
        page = templates.Loader().find_page(request.path).content
    except TemplateDoesNotExist:
        raise Http404
    
    t = Template(page)
    c = RequestContext(request)
    return HttpResponse(t.render(c), mimetype='text/html')
       
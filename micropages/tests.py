from django.http import HttpResponse, Http404
from django.test import TestCase
from django.template import TemplateDoesNotExist, TemplateSyntaxError
from django.test.client import RequestFactory
from django.contrib.admin.sites import AdminSite

import re

import micropages.templates
import micropages.models
import micropages.views
import micropages.admin

class AdminTests(TestCase):
    fixtures = ['micropages_test.json']

    def setUp(self):        
        self.factory = RequestFactory()    
        self.site = AdminSite()
        self.page = micropages.templates.Loader().find_page('/admin-page/')

    def test_should_return_not_supportsed_on_non_post_preview(self):
        request = self.factory.get('/admin/micropages/page/preview/')
        response = micropages.admin.PageAdmin(self.page, self.site).preview(request)
        self.assertEqual(response.status_code, 405)

    def test_should_return_500_if_previews_page_missing(self):
        request = self.factory.post('/admin/micropages/page/preview/')
        response = micropages.admin.PageAdmin(self.page, self.site).preview(request)
        self.assertEqual(response.status_code, 500)

    def test_should_return_200_page_preview(self):
        request = self.factory.post('/admin/micropages/page/preview/', {'page': 'admin'})
        response = micropages.admin.PageAdmin(self.page, self.site).preview(request)
        self.assertEqual(response.status_code, 200)

    def test_should_process_template_on_page_preview(self):
        request = self.factory.post('/admin/micropages/page/preview/', {'page': 'admin'})
        response = micropages.admin.PageAdmin(self.page, self.site).preview(request)
        self.assertEqual(response.content, 'admin')


class ModelsTest(TestCase):
    fixtures = ['micropages_test.json']

    def test_should_default_version_to_one(self):
        self.assertEqual(micropages.models.Page().version, 1)

    def test_should_increment_last_used_version(self):
        version = micropages.templates.Loader().find_page('/add-version/').copy_as_version()
        self.assertEqual(version.version, 3)

    def test_should_remember_base_version(self):
        version = micropages.templates.Loader().find_page('/add-version/').copy_as_version()
        self.assertEqual(version.branched_from, 1)

    def test_should_clear_published_flag_on_version(self):
        version = micropages.templates.Loader().find_page('/add-version/').copy_as_version()
        self.assertEqual(version.published, False)

    def test_should_switch_published_version(self):
        loader = micropages.templates.Loader()
        micropages.models.Page.objects.publish(loader.find_page('/publish/@2'))
        self.assertEqual(loader.find_page('/publish/@1').published, False)
        self.assertEqual(loader.find_page('/publish/@2').published, True)

    def test_should_not_modify_unrelated_pages_on_publish(self):
        loader = micropages.templates.Loader()
        micropages.models.Page.objects.publish(loader.find_page('/publish-this/@1'))
        self.assertEqual(loader.find_page('/donot-unpublish-this/@1').published, True)


class TemplatesTest(TestCase):
    fixtures = ['micropages_test.json']

    def setUp(self):        
        self.factory = RequestFactory()
    
    def test_should_match_one_page_without_version(self):
        r = re.compile(micropages.templates.url_pattern_compiled)        	
        self.assertEqual(r.match('one').groups(), ('one', None))

    def test_should_match_long_path_without_version(self):
        r = re.compile(micropages.templates.url_pattern_compiled)        	
        self.assertEqual(r.match('one/two/three').groups(), ('one/two/three', None))

    def test_should_not_match_nonnumeric_version(self):
        r = re.compile(micropages.templates.url_pattern_compiled)
        self.assertEqual(r.match('one@alpha'), None)

   	def test_should_match_one_page_with_version(self):
        r = re.compile(micropages.templates.url_pattern_compiled)        	
        self.assertEqual(r.match('one@1').groups(), ('one', '1'))

    def test_should_match_long_path_with_version(self):
        r = re.compile(micropages.templates.url_pattern_compiled)        	
        self.assertEqual(r.match('one/two/three@2').groups(), ('one/two/three', '2'))

    def test_should_load_fixture_data(self):
        self.assertTrue(len(micropages.models.Page.objects.all()) > 0)

    def test_should_find_most_recent_published_page(self):
        loader = micropages.templates.Loader()
        page = loader.find_page('/templates/base/')
        self.assertEqual(page.content, '/templates/base/@3')

    def test_should_find_specific_page_unpublished_version(self):
        loader = micropages.templates.Loader()        
        page = loader.find_page('/templates/base/@2')
        self.assertEqual(page.content, '/templates/base/@2')

    def test_should_find_specific_page_published_version(self):
        loader = micropages.templates.Loader()        
        page = loader.find_page('/templates/base/@1')
        self.assertEqual(page.content, '/templates/base/@1')

    def test_should_fail_on_missing_published_page(self):
        with self.assertRaises(TemplateDoesNotExist):
            loader = micropages.templates.Loader()        
            page = loader.find_page('/unknown')

    def test_should_fail_on_missing_specific_page(self):
        with self.assertRaises(TemplateDoesNotExist):
            loader = micropages.templates.Loader()        
            page = loader.find_page('/unknown/@1')

    def test_should_return_404_when_page_is_not_found(self):
        with self.assertRaises(Http404):
            request = self.factory.get('/unknown/')
            response = micropages.views.page(request)

    def test_should_return_200_when_page_is_found(self):
        request = self.factory.get('/insert-block/')
        response = micropages.views.page(request)
        self.assertEqual(response.status_code, 200)

    def test_should_apply_template_to_a_page(self):
        request = self.factory.get('/insert-block/')
        response = micropages.views.page(request)
        self.assertEqual(response.content, "before middle after")

    def test_should_generate_template_syntax_error(self):
        with self.assertRaises(TemplateSyntaxError):
            request = self.factory.get('/syntax-error/')
            response = micropages.views.page(request) 
            
    def test_should_fail_on_unknown_base_template(self):
        with self.assertRaises(TemplateDoesNotExist):
            request = self.factory.get('/unknown-base/')
            response = micropages.views.page(request)  
            
    def test_should_allow_to_extend_specific_version(self):
        request = self.factory.get('/extend-version/')
        response = micropages.views.page(request)
        self.assertEqual(response.content, "blocks@2")  



    




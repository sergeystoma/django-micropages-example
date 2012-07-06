# Why Micropages #

In a world with CMS ranging from Octopress, publishing with Jekyll via Dropbox, up to projects like Django CMS, I wanted a simple way of updating my sites, uncumbered with complex workflows, updateable without logging in to a server. I am already using Django, and I am a developer, so I am fine publishing with just Django templates. flatpages would work, but I didn't to SSH every time I needed to do a page change, thus Micropages was born.

Micropages provides a simple way to edit your site pages online using Django Admin, in a nice visual editor with syntax highlighting and realtime preview.

![Editor](https://github.com/underclouds/django-micropages-example/raw/master/readme-images/micropages_example.png)

# Django Version

Last tested on 1.3.1.

# Installing Example Application #

$ git clone git://github.com/underclouds/django-micropages-example.git
$ cd django-micropages-example
$ pip install -r pip-requirements.txt
$ cp settings_example.py settings.py
$ python manage.py syncdb
$ python manage.py test
$ python manage.py loaddata ./fixtures/example.json
$ python manage.py runserver 0:8080

Open http://yourbrowser:8080 and look around.

# Editing and Publishing #

Create a new page using Django Admin and edit away. Give page a URL and you almost ready to go. Until page is published, it is accessible only by using a version specifier, for example /home/@1. Once published using an admin action, latest version of the page will be served at the version-less URL.

# Stylesheets and JavaScript #

Micropages is purely an online editor on top of django templates, so at the moment editing is limited to just content pages. Build your stylesheets and scripts separately in deploy them via staticfiles facility.

# Reusing Pages #

You can include one micropage into another with include tag, e.g.:

    {% include '/reused/footer/' %}

# Caching #

There is no built in facility for caching, but you are free to use django templates caching. This will require some cache configuration in your settings.py (you should do it anyway), and when it is done, use tags to wrap cachable content:

    {% load cache %}
    {% cache 3600 footer %}

    cache me

    {% endcache %}

# Grappelli

Gorgeous Grappelli admin UI theme is fully supported.

# URLs and Trailing Slash Handling #

All URLS in Micropages are treated verbatim, without any additional preprocessing. This means that template and page locations should follow the URL scheme of your choosing. For example, if your site URLs are expected to end with a trailing slash, so should page locations as well. Redirect non-conformant URLs using your web server.

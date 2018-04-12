import urllib3.contrib.pyopenssl
from django.conf import settings
from django.contrib import admin
from django.http import HttpResponseServerError
from django.template import loader, TemplateDoesNotExist
from django.urls import include, path
from rest_framework_swagger.views import get_swagger_view

# Patch SSL requests issue
from leopay.views import get_tasks_log

urllib3.contrib.pyopenssl.inject_into_urllib3()

schema_view = get_swagger_view(title='Nicecode Automation API')

urlpatterns = [
    path('apidocs/', schema_view),
    path('admin/', admin.site.urls),
    path('api/v1/', include('leopay.api_urls')),
]

if settings.DEBUG:
    urlpatterns += [path('admin/tasks/log/', get_tasks_log, name="tasks-log")]

admin.autodiscover()
admin.site.site_header = 'Платежная система LeoPay'


def handler500(request, template='error500.html'):
    try:
        template = loader.get_template(template)
    except TemplateDoesNotExist:
        return HttpResponseServerError('<h1>Server Error (500)</h1>', content_type='text/html')
    return HttpResponseServerError(template.render())

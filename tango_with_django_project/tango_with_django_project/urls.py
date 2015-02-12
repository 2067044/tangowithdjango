from django.conf.urls import patterns, include, url
from django.contrib import admin

# Debug imports
from django.conf import settings
from django.conf.urls.static import static
from registration.backends.simple.views import RegistrationView  # Used for redux registration redirection to home
from django.contrib.auth import views as auth_views

# New class that redirects user to index page if successful login
class MyRegistrationView(RegistrationView):
    def get_success_url(self, request, user):
        return '/rango/'


urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^rango/', include('rango.urls')),
    # Used to override the default patter in django-registration-redux
    url(r'^accounts/register/$', MyRegistrationView.as_view(), name='registration_register'),
    url(r'^accounts/', include('registration.backends.simple.urls')),  # Registration redux
)


# Handle debug mode
if not settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Handle media
if settings.DEBUG:
    urlpatterns += patterns(
        'django.views.static',
        (r'^media/(?P<path>.*)',
        'serve',
        {'document_root': settings.MEDIA_ROOT}), )

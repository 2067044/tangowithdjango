from django.conf.urls import patterns, url
from rango import views

urlpatterns = patterns('',
        url(r'^$', views.index, name='index'),
        url(r'^about/$', views.about, name='about'),
        url(r'^add_category/$', views.add_category, name='add_category'),
        # Add a new page to a specific category based on the slug; note regex
        url(r'^category/(?P<category_name_slug>[\w\-]+)/add_page/$', views.add_page, name='add_page'),
        # View a specific category
        url(r'^category/(?P<category_name_slug>[\w\-]+)/$', views.category, name='category'),
        url(r'^restricted/', views.restricted, name='restricted'),  # This URL can only be accessed if user is logged in
        #url(r'^search/', views.search, name='search'),
        url(r'goto/$', views.track_url, name='goto'),
        url(r'register_profile/', views.register_profile, name='register_profile'),
        url(r'profile/', views.edit_profile, name='profile'),
        url(r'browse_profiles/', views.browse_profiles, name='browse_profiles')
        )



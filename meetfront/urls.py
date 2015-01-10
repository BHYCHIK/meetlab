from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'meetlab.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^$', 'meetfront.views.index', name='index_page'),
    url(r'^logout/$', 'meetfront.views.logout', name='logout_page'),
    url(r'^login/$', 'meetfront.views.login', name='login_page'),
    url(r'^register/$', 'meetfront.views.register', name='register_page'),
    url(r'^places/watch/(?P<page_id>\d+)$', 'meetfront.views.places', name='places_page'),
    url(r'^places/add/$', 'meetfront.views.place_add', name='add_places_page'),
    url(r'^places/edit/$', 'meetfront.views.place_edit', name='edit_places_page'),
    url(r'^plans/watch/(?P<page_id>\d+)$', 'meetfront.views.plans', name='plans_page'),
    url(r'^plans/add/$', 'meetfront.views.plans_add', name='add_plans_page'),
    url(r'^plans/edit/$', 'meetfront.views.plans_edit', name='edit_plans_page'),
    url(r'^plans/delete/$', 'meetfront.views.plans_delete', name='delete_plans_page'),


)

from django import urls
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views

urlpatterns=[
    path("",views.index_view,name='index_view'),
    path('login', views.login_view, name='login'),
    path('signup', views.signup, name='signup'),
    path('logout/', views.logout, name='logout'),
    path('dashboard/', views.admin_dashboard_view, name='a_dash'),
    path('manage_users/', views.manage_users_view, name='manage_users'),
    path('users/<int:user_id>/delete/',views.delete_user_view, name='delete_user'),
    path('upload/', views.upload_slip, name='upload'),
    path('my-slips/', views.user_slips, name='user_slips'),
    path('all-slips/', views.admin_slips_view, name='a_slips'),
    path('slips/<int:slip_id>/approve/', views.approve_slip, name='approve_slip'),
    path('slips/<int:slip_id>/reject/', views.reject_slip, name='reject_slip'),
    path('slips/<int:slip_id>/delete/', views.delete_slip, name='delete_slip'),
    path('dashboard/slips/locations/', views.admin_location_view, name='admin_slips_locations'),
    path('dashboard/slips/location/<str:location>/', views.admin_slips_by_location_view, name='slips_by_location'),


]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
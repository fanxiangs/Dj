from django.urls import path

from . import views
# from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.index, name='index'),

    path('login_page/', views.login_page, name='login_page'),
    path('register_page/', views.register_page, name='reg_page'),

    path('register/', views.register, name='register'),
    path('user_login/', views.user_login, name='login'),
    path('user_logout/', views.user_logout, name='logout'),

    path('bulletins/', views.bulletins, name='bulletins'),
    path('bulletin/<int:id>', views.bulletin, name='bulletin'),

    path('about_ci/', views.about, name='about'),
    path('contact_us/',views.contact, name='contact'),
    path('daily_info/',views.daily, name='daily'),
    path('ci_faq',views.faq, name='ci_faq'),
    path('static_check',views.static, name='static'),

    path('ver_maker/', views.maker, name='maker'),
    path('ver_maker/<int:project_id>', views.detail, name='detail'),

    path('ver_maker/<int:project_id>/check_sync', views.check_sync_status, name='check_sync'),
    path('ver_maker/<int:project_id>/check_sync_rpm', views.check_sync_rpm, name='check_sync_rpm'),
    path('ver_maker/<int:project_id>/start_sync', views.start_sync, name='start_sync'),
    path('ver_maker/<int:project_id>/wait_sync_end=<build_id>', views.wait_sync_end, name='wait_sync_end'),

    path('ver_maker/<int:project_id>/check_build', views.check_build_status, name='check_build'),
    path('ver_maker/<int:project_id>/check_build_rpm', views.check_build_rpm, name='check_build_rpm'),
    path('ver_maker/<int:project_id>/start_build', views.start_build, name='start_build'),
    path('ver_maker/<int:project_id>/wait_build_end=<build_id>', views.wait_build_end, name='wait_build_end'),

    path('ver_maker/<int:project_id>/check_smoke=<para>', views.check_smoke_status, name='check_smoke'),
    path('ver_maker/<int:project_id>/check_smoke_rpm=<para>', views.check_smoke_rpm, name='check_smoke_rpm'),

    path('ver_maker/<int:project_id>/start_witen', views.start_witen, name='start_witen'),
    path('ver_maker/<int:project_id>/wait_witen_end=<build_id>', views.wait_witen_end, name='wait_witen_end'),

    path('ver_maker/<int:project_id>/start_btrunc', views.start_btrunc, name='start_btrunc'),
    path('ver_maker/<int:project_id>/wait_btrunc_end=<build_id>', views.wait_btrunc_end, name='wait_btrunc_end'),

    path('ver_maker/<int:project_id>/start_tgpp', views.start_tgpp, name='start_tgpp'),
    path('ver_maker/<int:project_id>/wait_tgpp_end=<build_id>', views.wait_tgpp_end, name='wait_tgpp_end'),

    path('ver_maker/<int:project_id>/query_smoke=<para>', views.query_smoke, name='query_smoke'),

    path('ver_maker/<int:project_id>/update=<para>', views.update, name='update'),
    path('ver_maker/<int:project_id>/stop=<para>', views.stop, name='stop'),
    path('ver_maker/<int:project_id>/mail', views.mail, name='mail'),
    path('add_data/',views.add_data,name='add_data'),
    path('search/',views.search,name='search'),
]
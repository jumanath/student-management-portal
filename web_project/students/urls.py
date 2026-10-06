from django.urls import path
from students import views

urlpatterns = [
    path('', views.login_page, name='login_page'),
    path('home/', views.home, name='home'),
    path('update/', views.update_student, name='update_student'),
    path('delete/',views.delete_student,name='delete_student'),
    path('export/',views.export_students,name='export_students')

]
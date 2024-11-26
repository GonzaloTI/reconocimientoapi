# import the path function from urls module to define url patterns
from django.urls import path

# import views from the current directory to use in url patterns
from . import views
# import specific views functions directly for easy access

# urlpatterns list to hold the url configurations
urlpatterns = [
    # routes to 'home' view and named as 'home'
    path('', views.home, name='home'),
    # routes to 'about' view and named as 'about'
    path('about/', views.about, name='about'),
    # routes to 'register' view and named as 'register'
    path('register/', views.register, name='register'),
    # routes to 'verify_email' view and named as 'verify_email'
    path('verify_email/', views.verify_email, name='verify_email'),
    # routes to 'user_login' view and named as 'login'
    path('login/', views.user_login, name='login'),
    
    path('analizar-imagen/', views.analizar_imagen, name='analizar_imagen'),
        
    path('Home_KPI/', views.KPIhome, name='homekpi'),
   
    # routes to 'signout' view and named as 'signout'
    path('signout/', views.signout, name='signout'),

  
 
    
]

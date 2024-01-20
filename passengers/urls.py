from django.urls import path
from .import views
urlpatterns = [
    path('signup/', views.SignupView.as_view(), name='signup'),
    path('active/<uidb64>/<token>/', views.userActivation, name = 'activate'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.userLogout, name='logout'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/update', views.update_profile, name='update_profile'),
    path('profile/password/update', views.password_change, name='update_password'),
    path('deposit/', views.DepositMoneyView.as_view(), name='deposit'),
]

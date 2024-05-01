from django.urls import path
from .views import CustomLoginView, CustomSignUpView, InitialPageView, UserPageView

app_name = 'authentication'

urlpatterns = [
    path('', InitialPageView.as_view(), name='index'),
    path('login/', CustomLoginView.as_view(), name='login'),  # Make sure this line exists
    path('signup/', CustomSignUpView.as_view(), name='signup'),
    path('user/<int:pk>/', UserPageView.as_view(), name='user_page'),
]

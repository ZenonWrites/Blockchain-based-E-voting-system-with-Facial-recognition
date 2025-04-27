"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework import routers
from main.views import request_otp, verify_otp
from knox import views as knox_views
# Removed unused import for TokenAuthentication
from django.conf import settings
from django.conf.urls.static import static
from main import views
from main.views import (
    UserViewSet, ElectionViewSet, CandidateViewSet, BlockchainTransactionViewSet, VoteViewSet,
    request_otp, verify_otp,CheckPhoneNumberView,LoginAPI, PhoneOTPLoginAPI, UserDetailAPI, VotingResultViewSet, open_voting
)
#from main.views import LoginView


router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'elections', views.ElectionViewSet)
router.register(r'candidates', views.CandidateViewSet)
router.register(r'blockchain-transactions', views.BlockchainTransactionViewSet)
router.register(r'votes', views.VoteViewSet)
router.register(r'voting-results', views.VotingResultViewSet, basename='voting-results')

#router.register(r'groups', views.GroupViewSet)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('main/', include('main.urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path("api/request-otp/", request_otp, name="request-otp"),
    path("api/verify-otp/", verify_otp, name="verify-otp"),
    path('logout/',knox_views.LogoutView.as_view(), name='knox_logout'), 
    path('logoutall/',knox_views.LogoutAllView.as_view(), name='knox_logoutall'), 
    path('api/password_reset/',include('django_rest_passwordreset.urls', namespace='password_reset')), 
    path('api/verification/', include('verification.urls')),
    path('api/', include('main.urls')),
    path('api/check-phone-number/', CheckPhoneNumberView.as_view()),
 #  path('api/get-user-by-phone-number/', GetUserByPhoneNumberView.as_view()),
    path('api/auth/login/', LoginAPI.as_view(), name='login'),
   # path('api/auth/otp-login/', otp_login, name='knox_otp_login'),
    path('api/auth/phone-login/', PhoneOTPLoginAPI.as_view(), name='knox_phone_login'),
    path('api/auth/logout/', knox_views.LogoutView.as_view(), name='knox_logout'),
    path('api/auth/logoutall/', knox_views.LogoutAllView.as_view(), name='knox_logoutall'),
    path('api/auth/user/', UserDetailAPI.as_view(), name='auth-user'),
   # path('api/vote-result/',VotingResultViewSet.as_view({'get': 'list'}), name='vote-result'),
    path('api/open-voting/', open_voting, name='open-voting'),
    
]
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'elections', ElectionViewSet)
router.register(r'candidates', CandidateViewSet)
router.register(r'transactions', BlockchainTransactionViewSet)
router.register(r'votes', VoteViewSet)
router.register('register', RegisterViewset, basename='register')
router.register('login', LoginViewset, basename='login')
router.register(r'voting-results', VotingResultViewSet, basename='voting-results')

urlpatterns = [
    path('', include(router.urls)),
    path('profile/', profile, name='profile'),
    path('phone-numbers/', PhoneNumberListView.as_view()),
   # path('user/by-phone-number/', get_user_by_phone_number),
    
    
]
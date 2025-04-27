# verification/urls.py
from django.urls import path
from .views import UploadIDDocumentView, UploadSelfieView, VerificationStatusView

urlpatterns = [
    path('upload-id/', UploadIDDocumentView.as_view(), name='upload-id'),
    path('upload-selfie/', UploadSelfieView.as_view(), name='upload-selfie'),
    path('status/', VerificationStatusView.as_view(), name='verification-status'),
]

# identity_verification_system/urls.py


# Add this to serve media files in development

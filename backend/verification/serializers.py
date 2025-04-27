from rest_framework import serializers
from .models import VerificationRequest

class VerificationRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = VerificationRequest
        fields = [
            'id', 'created_at', 'status', 'document_type', 
            'document_number', 'full_name', 'date_of_birth', 
            'face_match'
        ]
        read_only_fields = ['id', 'created_at', 'status']
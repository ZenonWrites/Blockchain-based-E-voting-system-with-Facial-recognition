from django.db import models
import uuid

class VerificationRequest(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('verified', 'Verified'),
        ('failed', 'Failed'),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Document information extracted from OCR
    document_type = models.CharField(max_length=50, null=True, blank=True)
    document_number = models.CharField(max_length=100, null=True, blank=True)
    full_name = models.CharField(max_length=255, null=True, blank=True)
    date_of_birth = models.CharField(max_length=50, null=True, blank=True)
    
    # Face match result
    face_match = models.BooleanField(null=True, blank=True)
    
    # Temporary image storage (will be deleted after processing)
    id_document = models.ImageField(upload_to='documents/', null=True)
    selfie_image = models.ImageField(upload_to='selfies/', null=True)
    
    def __str__(self):
        return f"Verification {self.id} - {self.status}"
    
    def save(self, *args, **kwargs):
        # Delete images after verification is complete
        if self.status in ['verified', 'failed'] and not self._state.adding:
            # Get the old instance to check if images exist
            old_instance = VerificationRequest.objects.get(pk=self.pk)
            if old_instance.id_document:
                old_instance.id_document.delete(save=False)
            if old_instance.selfie_image:
                old_instance.selfie_image.delete(save=False)
            self.id_document = None
            self.selfie_image = None
        
        super().save(*args, **kwargs)
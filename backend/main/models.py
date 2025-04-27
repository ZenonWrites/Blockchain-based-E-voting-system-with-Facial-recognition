from django.db import models
import random
import hashlib
import json
from django.core.exceptions import ValidationError
from django.utils.timezone import now
from datetime import timedelta
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager
import uuid
from django_rest_passwordreset.signals import reset_password_token_created
from django.dispatch import receiver 
from django.urls import reverse 
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags

class CustomUserManager(BaseUserManager): 
    def create_user(self, email, password=None, **extra_fields ): 
        if not email: 
            raise ValueError('Email is a required field')
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self,email, password=None, **extra_fields): 
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

'''
class CustomUser(AbstractUser):
    email = models.EmailField(max_length=200, unique=True)
    username = models.CharField(max_length=200, null=True, blank=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        db_table = 'main_user'

@receiver(reset_password_token_created)
def password_reset_token_created(reset_password_token, *args, **kwargs):
    sitelink = "http://localhost:5173/"
    token = "{}".format(reset_password_token.key)
    full_link = str(sitelink)+str("password-reset/")+str(token)

    print(token)
    print(full_link)

    context = {
        'full_link': full_link,
        'email_adress': reset_password_token.user.email
    }

    html_message = render_to_string("backend/email.html", context=context)
    plain_message = strip_tags(html_message)

    msg = EmailMultiAlternatives(
        subject = "Request for resetting password for {title}".format(title=reset_password_token.user.email), 
        body=plain_message,
        from_email = "sender@example.com", 
        to=[reset_password_token.user.email]
    )

    msg.attach_alternative(html_message, "text/html")
    msg.send()
'''

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('voter', 'Voter'),
        ('candidate', 'Candidate'),
    )
    username = models.CharField(max_length=30, unique=True)
    email = models.EmailField(max_length=254, unique=True)
    wallet_address = models.CharField(max_length=100, blank=True, null=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='voter')
    voter_id = models.CharField(max_length=20, unique=True)
    phone_number = models.CharField(max_length=10, unique=True)
    address = models.TextField(blank=True, null=True, default="Plz enter your address")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    adhaar_number = models.CharField(max_length=12, unique=True, null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    
    # Add missing is_staff field
    is_staff = models.BooleanField(default=True)  # Allows admin access to Django Admin panel
    
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='main_user_set',
        blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='main_user_permissions',
        blank=True
    )

    def __str__(self):
        return self.username

    class Meta:
        db_table = 'main_user'

class Election(models.Model):
    name = models.CharField(max_length=100,unique=True)
    description = models.TextField()
    candidates = models.ManyToManyField(CustomUser, related_name='election_candidates')  # Custom related_name to avoid conflict
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    voters = models.ManyToManyField(
        'CustomUser',
        related_name='voted_elections',
        blank=True
    )

    def __str__(self):
        return self.name


class Party(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Candidate(models.Model):
    
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    election = models.ForeignKey(Election, on_delete=models.CASCADE, related_name='candidate_list')  # Custom related_name to avoid conflict
    party = models.ForeignKey(Party, on_delete=models.SET_NULL, null=True, blank=True, related_name='candidates')
    manifesto = models.TextField(blank=True, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['election', 'party'], name='unique_candidate_per_party_in_election', condition=~models.Q(party=None))
        ]

    def clean(self):
        if not self.party and Candidate.objects.filter(election=self.election, user=self.user).exists():
            raise ValidationError("A candidate must either belong to a party or be independent.")
    
    def __str__(self):
        return f"{self.user.username} - {self.election.name} ({self.party.name if self.party else 'Independent'})"


class BlockchainTransaction(models.Model):
    transaction_hash = models.CharField(max_length=64, unique=True)
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sent_transactions')
    receiver = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='received_transactions')
    timestamp = models.DateTimeField(auto_now_add=True)
    data = models.JSONField()
    
    def __str__(self):
        return self.transaction_hash
    
    def save(self, *args, **kwargs):
        if not self.transaction_hash:
            self.transaction_hash = self.generate_hash()
        super().save(*args, **kwargs)
    
    def generate_hash(self):
        data_string = json.dumps(self.data, sort_keys=True) + str(self.timestamp)
        return hashlib.sha256(data_string.encode()).hexdigest()


class Vote(models.Model):
    voter = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='votes')  # Custom related_name for reverse accessor
    election = models.ForeignKey(Election, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='votes')  # Custom related_name for reverse accessor
    transaction = models.ForeignKey(BlockchainTransaction, on_delete=models.CASCADE, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('voter', 'election')  # Ensures a voter votes only once per election
    
    def __str__(self):
        return f"{self.voter.username} voted for {self.candidate.username} in {self.election.name}"


class OTP(models.Model):
    phone_number = models.CharField(max_length=15, unique=True)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        return now() - self.created_at < timedelta(minutes=5)  # OTP valid for 5 minutes
    

class VotingResult(models.Model):
    election = models.ForeignKey('Election', on_delete=models.CASCADE)
    winner = models.ForeignKey('Candidate', on_delete=models.CASCADE, null=True, blank=True)
    total_votes = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.election.name} - {self.winner.user.username if self.winner else 'No winner'}"

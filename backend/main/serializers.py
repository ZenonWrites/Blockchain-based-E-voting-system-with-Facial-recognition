from rest_framework import serializers
from .models import * 
from django.contrib.auth import get_user_model 
from rest_framework.validators import UniqueTogetherValidator

User = get_user_model()

class LoginSerializer(serializers.Serializer):
    phone_number = serializers.IntegerField(required=True)

    class Meta:
        model = User
        fields = ['phone_number']

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        return ret
    



    
class RegisterSerializer(serializers.ModelSerializer):
    class Meta: 
        model = User
        fields = ('id', 'username', 'role', 'wallet_address', 'voter_id',
                  'phone_number', 'address', 'adhaar_number', 'is_verified', 'email')
    
    def validate_email(self, value):
        if not value:
            raise serializers.ValidationError("Email is required.")
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user
class UserSerializer(serializers.ModelSerializer):

    def get_queryset(self):
        queryset = CustomUser.objects.all()
        phone_number = self.request.query_params.get('phone_number')
        if phone_number:
            queryset = queryset.filter(phone_number=phone_number)
        return queryset

    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email', 'role', 'wallet_address', 'voter_id',
            'phone_number', 'address', 'created_at', 'updated_at', 
            'adhaar_number','is_verified', 'is_staff' # Include is_staff
        ]
        read_only_fields = ['created_at', 'updated_at']

class ElectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Election
        fields = ['id', 'name', 'description', 'start_date', 'end_date', 'created_at']


class PartySerializer(serializers.ModelSerializer):
    class Meta:
        model = Party
        fields = ['id', 'name']

class CandidateSerializer(serializers.ModelSerializer):
    party = PartySerializer(read_only=True)
    party_id = serializers.PrimaryKeyRelatedField(
        queryset=Party.objects.all(), write_only=True, required=False, allow_null=True
    )
    election = serializers.PrimaryKeyRelatedField(queryset=Election.objects.all())
    user_name = serializers.CharField(source='user.username', read_only=True)
    party_name = serializers.CharField(source='party.name', read_only=True)
    
    class Meta:
        model = Candidate
        fields = ['id', 'user_name', 'election', 'party', 'party_id', 'manifesto', 'party_name']

    def validate(self, data):
        """
        Ensure that a candidate is either independent or from a party and 
        that only one candidate can stand from a party in a given election.
        """
        election = data.get('election')
        party = data.get('party_id')

        if not party and Candidate.objects.filter(election=election, user=self.context['request'].user).exists():
            raise serializers.ValidationError("A candidate must either belong to a party or be independent.")

        if party and Candidate.objects.filter(election=election, party=party).exists():
            raise serializers.ValidationError("Only one candidate can stand from a party in a given election.")

        return data

    def create(self, validated_data):
        party = validated_data.pop('party_id', None)
        candidate = Candidate.objects.create(party=party, **validated_data)
        return candidate

    def update(self, instance, validated_data):
        party = validated_data.pop('party_id', None)
        instance.party = party
        instance.election = validated_data.get('election', instance.election)
        instance.manifesto = validated_data.get('manifesto', instance.manifesto)
        instance.save()
        return instance
class BlockchainTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlockchainTransaction
        fields = ['id', 'transaction_hash', 'sender', 'receiver', 'timestamp', 'data']

class VoteSerializer(serializers.ModelSerializer):
    voter = serializers.HiddenField(default=serializers.CurrentUserDefault())
    transaction = BlockchainTransactionSerializer(read_only=True)

    # Make sure to include this field in Meta.fields!
    candidate_id = serializers.PrimaryKeyRelatedField(
        queryset=Candidate.objects.all(),
        write_only=True
    )
    election = serializers.PrimaryKeyRelatedField(queryset=Election.objects.all())


    class Meta:
        model  = Vote
        fields = [
            'id', 'voter', 'transaction',
            'election', 'candidate_id', 'timestamp'
        ]
        validators = [
            UniqueTogetherValidator(
                queryset=Vote.objects.all(),
                fields=['voter', 'election'],
                message="You may only vote once per election."
            )
        ]

    def create(self, validated_data):
        candidate_obj = validated_data.pop('candidate_id')
        transaction = validated_data.pop('transaction')
        # voter and transaction come from .save(...) in the view
        voter = self.context['request'].user
        vote = Vote.objects.create(
            candidate=candidate_obj,voter=voter,transaction=transaction,
            **validated_data
        )
        return vote

class VerifyOtpSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    otp = serializers.CharField()

    def validate(self, data):
        if not data.get('phone_number'):
            raise serializers.ValidationError({'phone_number': 'Phone number is required'})
        if not data.get('otp'):
            raise serializers.ValidationError({'otp': 'OTP is required'})
        return data
    
class VotingResultSerializer(serializers.ModelSerializer):
    election    = ElectionSerializer(read_only=True)
    winner      = CandidateSerializer(read_only=True)
    class Meta:
        model = VotingResult
        fields = ['id', 'election', 'winner', 'total_votes', 'created_at']

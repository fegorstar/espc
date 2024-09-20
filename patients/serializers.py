from cloudinary.uploader import destroy
from rest_framework import status
from django.db import transaction, models
from django.core.exceptions import ValidationError
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.db.models import Sum
import cloudinary.uploader
from rest_framework import serializers
from accounts.models import User
from django.conf import settings
from patients.models import Profile
from accounts.models import User


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=False)
    user_type = serializers.CharField(read_only=True)
    is_active = serializers.BooleanField(read_only=True)

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'user_type', 'is_active']
class ProfileUpdateSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='user.first_name', required=True)
    last_name = serializers.CharField(source='user.last_name', required=True)
    nin = serializers.CharField(required=False)
    state = serializers.CharField(required=True)
    city = serializers.CharField(required=True)
    profile_picture = serializers.ImageField(required=False)

    class Meta:
        model = Profile
        fields = ['first_name', 'last_name', 'profile_picture',
                  'state', 'city', 'phone_number', 'nin']
        read_only_fields = ['user_id', 'email']

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        if user_data:
            user = instance.user
            user.email = user_data.get('email', user.email)
            user.first_name = user_data.get('first_name', user.first_name)
            user.last_name = user_data.get('last_name', user.last_name)
            user.save()

        profile_picture = validated_data.get('profile_picture')
        if profile_picture:
            # Ensure the previous picture is removed from Cloudinary if applicable
            if instance.profile_picture and hasattr(instance.profile_picture, 'public_id'):
                cloudinary.uploader.destroy(instance.profile_picture.public_id)
            # Save the new profile picture
            instance.profile_picture = profile_picture

        instance.state = validated_data.get('state', instance.state)
        instance.city = validated_data.get('city', instance.city)
        instance.phone_number = validated_data.get('phone_number', instance.phone_number)
        instance.nin = validated_data.get('nin', instance.nin)

        instance.save()
        instance.refresh_from_db()
        return instance

class ProfileSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    profile_picture = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ['user', 'profile_picture', 'state', 'city', 'phone_number', 'nin',
                  'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

    def get_user(self, obj):
        user = obj.user
        return {
            'id': user.id,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'user_type': user.user_type,
            'is_active': user.is_active,
        }

    def get_profile_picture(self, obj):
        if obj.profile_picture:
            return obj.profile_picture.url
        return None


class EmailChangeSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(min_length=6, max_length=68)


class PasswordChangeSerializer(serializers.Serializer):
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

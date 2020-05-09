from django.contrib.auth.models import User
from rest_framework import serializers
from django.db import transaction
from django.shortcuts import get_object_or_404

from apps.users.models import *

class UserSerializer(serializers.HyperlinkedModelSerializer):
    profile = serializers.HyperlinkedRelatedField(view_name="profile-detail", queryset=Profile.objects.all())

    class Meta:
        model = User
        fields = ['profile', 'username', 'first_name', 'last_name', 'email', 'is_active', 'date_joined']


class ProfileSerializer(serializers.HyperlinkedModelSerializer):
    usertypes = serializers.HyperlinkedRelatedField(many=True, view_name='usertype-detail', queryset=UserType.objects.all())
    groups = serializers.HyperlinkedRelatedField(many=True, view_name='group-detail', queryset=Group.objects.all())
    friends = serializers.HyperlinkedRelatedField(many=True, view_name='profile-detail', queryset=Profile.objects.all())

    user = UserSerializer(read_only=True)

    class Meta:
        model = Profile
        fields = '__all__'

class UserTypeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = UserType
        fields = '__all__'

class GroupSerializer(serializers.HyperlinkedModelSerializer):
    owner = serializers.HyperlinkedRelatedField(view_name='profile-detail', read_only=True)

    def create(self, validated_data):
        current_profile = Profile.objects.get(user=self.context['request'].user)

        members = validated_data.pop('members') if 'members' in validated_data else []
        members.append(current_profile)

        group = Group.objects.create(owner=current_profile)

        group.members.set(members)

        return group

    class Meta:
        model = Group
        fields = '__all__'







from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from apps.accounts.models import University, Profile, ResetPasswordToken


class UniversitySerializer(serializers.ModelSerializer):

    class Meta:
        model = University
        fields = ['name']


class ProfileSerializer(serializers.ModelSerializer):
    uni = serializers.CharField(required=False)

    class Meta:
        model = Profile
        exclude = ['user']

    def check_uni(self, uni_name):
        uni = University.objects.filter(name=uni_name)
        if uni.count() != 1:
            raise serializers.ValidationError('University with given name not found.')
        return uni.get()

    def validate(self, data):
        if 'uni' not in data:
            return data
        self.check_uni(data['uni'])
        return data

    def create(self, validated_data):
        uni = self.check_uni(validated_data.pop('uni'))
        validated_data['uni'] = uni
        validated_data['user'] = self.user
        return Profile.objects.create(**validated_data)

    def update(self, instance, validated_data):
        profile = instance
        profile.firstname_fa = validated_data.get('firstname_fa', profile.firstname_fa)
        profile.firstname_en = validated_data.get('firstname_en', profile.firstname_en)
        profile.lastname_fa = validated_data.get('lastname_fa', profile.lastname_fa)
        profile.lastname_en = validated_data.get('lastname_en', profile.lastname_en)
        profile.birth_date = validated_data.get('birth_date', profile.birth_date)
        profile.university = validated_data.get('university', profile.university)
        profile.bmp = validated_data.get('bmp', profile.bmp)
        profile.major = validated_data.get('major', profile.major)
        profile.student_id = validated_data.get('student_id', profile.student_id)
        profile.phone_number = validated_data.get('phone_number', profile.phone_number)
        if 'uni' in validated_data:
            print(validated_data['uni'])
            profile.uni = self.check_uni(validated_data.get('uni'))
        profile.save()
        return profile


class UserSignUpSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()

    email = serializers.EmailField(validators=[UniqueValidator(queryset=User.objects.all())])

    password_1 = serializers.CharField(style={'input_type': 'password'})
    password_2 = serializers.CharField(style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ['username', 'email', 'password_1', 'password_2', 'profile']

    def validate(self, data):
        if data['password_1'] != data['password_2']:
            raise serializers.ValidationError('passwords don\'t match!')
        return data

    def create(self, validated_data):
        profile_data = validated_data.pop('profile')

        profile_serializer = ProfileSerializer(data=profile_data)
        if profile_serializer.is_valid(raise_exception=True):

            validated_data.pop('password_1')
            validated_data['password'] = make_password(validated_data.pop('password_2'))

            user = User.objects.create(**validated_data)
            profile_serializer.user = user
            profile_serializer.save()
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()

    class Meta:
        model = User
        fields = ['profile', 'email']

    def update(self, instance, validated_data):
        instance.email = validated_data.get('email', instance.email)
        instance.save()

        profile_data = validated_data.pop('profile')
        profile_serializer = ProfileSerializer(data=profile_data, instance=instance.profile)
        if profile_serializer.is_valid(raise_exception=True):
            profile_serializer.save()
        return instance


class ChangePasswordSerializer(serializers.Serializer):

    old_password = serializers.CharField(style={'input_type': 'password'})
    new_password1 = serializers.CharField(style={'input_type': 'password'})
    new_password2 = serializers.CharField(style={'input_type': 'password'})

    def validate(self, data):
        if data['new_password1'] != data['new_password2']:
            raise serializers.ValidationError('passwords don\'t match!')
        return data

class ResetPasswordSerializer(serializers.Serializer):

    email = serializers.EmailField()


class ResetPasswordConfirmSerializer(serializers.ModelSerializer):

    new_password1 = serializers.CharField(max_length=100)
    new_password2 = serializers.CharField(max_length=100)

    class Meta:
        model = ResetPasswordToken
        fields = ['new_password1', 'new_password2', 'uid', 'token']

    def validate(self, data):
        if data['new_password1'] != data['new_password2']:
            raise serializers.ValidationError('passwords don\'t match!')
        return data

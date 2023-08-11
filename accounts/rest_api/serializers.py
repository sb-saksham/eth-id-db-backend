from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField
from knox.models import AuthToken

from accounts.models import User, EmailActivation


class SignupSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField()

    class Meta:
        model = User
        fields = ("email", "full_name", "eth_wallet_address", "password", "password2")


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("email", "full_name", "eth_wallet_address", "password")


class LoginSerializer(serializers.Serializer):
    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    email = serializers.EmailField()
    password = serializers.CharField()

    def validate_email(self, email):
        """
        Check whether email is registered or not and whether User is active or not.
        :param email:
        :return: cleaned Email
        """
        email_exists = User.objects.email_exists(email=email)
        if not email_exists:
            raise serializers.ValidationError("Email Does Not exists")
        elif not email_exists.first().is_active:
            raise serializers.ValidationError("Account is not activated! Please activate your Account first.")
        return email

    def validate(self, data):
        user = User.objects.get(email=data['email'])
        data['user'] = user
        return data


class ReactivateEmailSerializer(serializers.Serializer):
    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    email = serializers.EmailField()

    def validate_email(self, email):
        qs = EmailActivation.objects.email_exists(email)
        if not qs.exists():
            raise serializers.ValidationError("Your Email does not exist! Please Register!")
        return email


# Verify Serializers
class IdImageSerializer(serializers.Serializer):
    def update(self, instance, validated_data):
        instance.id_image = validated_data.get("id_image")
        instance.name_check = validated_data.get("name_check")
        instance.save()
        return instance

    def create(self, validated_data):
        pass

    id_image = Base64ImageField()


class WalletImageSerializer(serializers.Serializer):
    def update(self, instance, validated_data):
        instance.waddr_image = validated_data.get("waddr_image")
        instance.face_check = validated_data.get("face_check")
        instance.waddr_check = validated_data.get("waddr_check")
        instance.save()
        return instance

    def create(self, validated_data):
        pass

    waddr_image = Base64ImageField()
    eth_name = serializers.CharField()


class FinalSaveToDbSerializer(serializers.Serializer):
    def update(self, instance, validated_data):
        instance.is_verified = validated_data.get("is_verified")
        instance.save()
        return instance

    def create(self, validated_data):
        pass

    ens = serializers.CharField(max_length=15)
    address = serializers.CharField(max_length=42)

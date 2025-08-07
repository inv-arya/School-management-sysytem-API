
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from accounts.models import User

class UserSerializer(serializers.ModelSerializer):
    password_confirm = serializers.CharField(write_only=True, required=False)  

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'password', 'password_confirm']
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def validate(self, data):
        password = data.get('password')
        password_confirm = data.get('password_confirm')

        # Only validate if password is provided
        if password:
            if password_confirm is not None and password != password_confirm:
                raise serializers.ValidationError({"password": "Passwords do not match."})

            user = self.instance or User(**data)
            try:
                validate_password(password, user=user)
            except ValidationError as e:
                raise serializers.ValidationError({"password": e.messages})

        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm', None)
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        validated_data.pop('password_confirm', None)
        password = validated_data.pop('password', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            try:
                validate_password(password, user=instance)
            except ValidationError as e:
                raise serializers.ValidationError({"password": e.messages})
            instance.set_password(password)

        instance.save()
        return instance

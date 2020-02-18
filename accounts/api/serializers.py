import re
from rest_framework import serializers

from accounts.models import User
User = User()


class UserDisplaySerializer(serializers.Serializer):
    id = serializers.SerializerMethodField(read_only=True)
    first_name = serializers.SerializerMethodField(read_only=True)
    last_name = serializers.SerializerMethodField(read_only=True)
    username = serializers.SerializerMethodField(read_only=True)
    email = serializers.SerializerMethodField(read_only=True)
    is_active = serializers.SerializerMethodField(read_only=True)
    date_joined = serializers.SerializerMethodField(read_only=True)

    def get_id(self, obj):
        return str(obj.get("_id"))

    def get_first_name(self, obj):
        return obj.get("first_name")

    def get_last_name(self, obj):
        return obj.get("last_name")

    def get_username(self, obj):
        return obj.get("username")

    def get_email(self, obj):
        return obj.get("email")

    def get_is_active(self, obj):
        return obj.get("is_active")

    def get_date_joined(self, obj):
        return obj.get("date_joined")


class UserRegisterSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=80)
    last_name = serializers.CharField(max_length=80)
    username = serializers.CharField(max_length=30)
    email = serializers.EmailField()
    password = serializers.CharField(style={"input_type": "password"}, write_only=True)
    password2 = serializers.CharField(label="password confirm", style={"input_type": "password"}, write_only=True)

    def validate_username(self, value):
        regex_username = re.compile("^{username}$".format(username=value), re.IGNORECASE)
        qs = User.collection.find({"username": regex_username})
        if qs.count():
            raise serializers.ValidationError("User with this username already exists.")
        return value

    def validate_email(self, value):
        regex_email = re.compile("^{email}$".format(email=value))
        qs = User.collection.find({"email": regex_email})
        if qs.count():
            raise serializers.ValidationError("User with this email already exists.")
        return value

    def validate(self, data):
        pw = data.get("password")
        pw2 = data.get("password2")
        if pw != pw2:
            raise serializers.ValidationError("Password must be match.")
        return data

    def create(self, validated_data):
        User.set_first_name(validated_data.get("first_name"))
        User.set_last_name(validated_data.get("last_name"))
        User.set_username(validated_data.get("username"))
        User.set_email(validated_data.get("email"))
        User.set_password(validated_data.get("password"))
        User.set_active()
        context = {
            "first_name": User.get_first_name(),
            "last_name": User.get_last_name(),
            "username": User.get_username(),
            "email": User.get_email(),
            "password": User.get_password(),
            "is_active": User.get_active(),
            "date_joined": User.get_date_joined()
        }
        u_id = User.save(context)
        User.set_id(u_id)
        return User

    # TODO: update doesn't work
    def update(self, instance, validated_data):
        user = User()
        instance["first_name"] = validated_data.get('first_name', instance.get("first_name"))
        instance["last_name"] = validated_data.get('last_name', instance.get("last_name"))
        instance["username"] = validated_data.get('username', instance.get("username"))
        instance["email"] = validated_data.get('email', instance.get("email"))
        instance["password"] = validated_data.get('password', instance.get("password"))

        user.set_first_name(instance.get("first_name"))
        user.set_last_name(instance.get("last_name"))
        user.set_username(instance.get("username"))
        user.set_email(instance.get("email"))
        user.set_password(instance.get("password"))

        data = {
            "first_name": user.get_first_name(),
            "last_name": user.get_last_name(),
            "username": user.get_username(),
            "email": user.get_email(),
            "password": user.get_password()
        }
        user.update({"_id": instance.get("_id")}, data)
        return instance

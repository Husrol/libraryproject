from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from rest_framework.exceptions import ValidationError
from .models import Book, AppUser

UserModel = get_user_model()

class UserRegisterSerializer(serializers.ModelSerializer):
	class Meta:
		model = UserModel
		fields = '__all__'
	def create(self, clean_data):
		user_obj = UserModel.objects.create_user(email=clean_data['email'], password=clean_data['password'])
		user_obj.username = clean_data['username']
		user_obj.save()
		return user_obj

class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
    is_staff = serializers.BooleanField(read_only=True)
    user_id = serializers.IntegerField(read_only=True)

    def check_user(self, clean_data):
        user = authenticate(username=clean_data['email'], password=clean_data['password'])
        if not user:
            raise ValidationError('User not found')
        return user

    def validate(self, data):
        # Kullanıcıyı doğrula ve döndür
        user = self.check_user(data)
        data['is_staff'] = user.is_staff
        data["user_id"] = user.user_id
        return data



class UserSerializer(serializers.ModelSerializer):
	class Meta:
		model = AppUser
		fields = ('email', 'username', "is_staff")

class AppUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppUser
        fields = ['user_id', 'email', 'username', 'is_staff']


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = "__all__"

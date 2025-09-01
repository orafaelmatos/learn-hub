from django.contrib.auth import authenticate, get_user_model

User = get_user_model()

class UserRepository:
    def create_user(self, validated_data):
        return User.objects.create_user(**validated_data)

    def authenticate_user(self, email, password):
        user = authenticate(username=email, password=password)
        if not user:
            raise ValueError("Invalid credentials")
        return user

    def change_password(self, user, new_password):
        user.set_password(new_password)
        user.save()

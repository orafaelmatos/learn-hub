from ..repositories.auth_repository import UserRepository
from ..serializers.auth_serializer import LoginSerializer
from ..utils.tokens import generate_tokens_for_user


class LoginUserService:
    def __init__(self):
        self.repository = UserRepository()

    def execute(self, data):
        serializer = LoginSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        user = self.repository.authenticate_user(
            email=serializer.validated_data['email'],
            password=serializer.validated_data['password']
        )
        tokens = generate_tokens_for_user(user)
        return user, tokens

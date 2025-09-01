from ..repositories.auth_repository import UserRepository
from ..serializers.auth_serializer import UserCreateSerializer
from ..utils.tokens import generate_tokens_for_user


class RegisterUserService:
    def __init__(self):
        self.repository = UserRepository()

    def execute(self, data):
        serializer = UserCreateSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        tokens = generate_tokens_for_user(user)
        return user, tokens

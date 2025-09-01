from django.contrib.auth import update_session_auth_hash

from ..repositories.auth_repository import UserRepository
from ..serializers.auth_serializer import PasswordChangeSerializer


class ChangePasswordService:
    def __init__(self):
        self.repository = UserRepository()

    def execute(self, user, data, request):
        serializer = PasswordChangeSerializer(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        self.repository.change_password(user, serializer.validated_data['new_password'])
        update_session_auth_hash(request, user)

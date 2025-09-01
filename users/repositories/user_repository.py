from ..models.user_model import User


class UserRepository:

    @staticmethod
    def get_teachers():
        return User.objects.filter(user_type='teacher').order_by('id')

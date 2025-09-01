from rest_framework_simplejwt.tokens import RefreshToken


def authenticate_user(validated_data):
    user = validated_data['user']
    return user

def generate_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

def change_user_password(user, new_password):
    user.set_password(new_password)
    user.save()

def blacklist_refresh_token(refresh_token):
    try:
        token = RefreshToken(refresh_token)
        token.blacklist()
    except Exception:
        pass

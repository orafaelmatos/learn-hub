from rest_framework_simplejwt.tokens import RefreshToken


def generate_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

def blacklist_refresh_token(token):
    try:
        token_obj = RefreshToken(token)
        token_obj.blacklist()
    except Exception:
        pass
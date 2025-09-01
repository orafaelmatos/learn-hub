from ..utils.tokens import blacklist_refresh_token


class LogoutUserService:
    def execute(self, refresh_token):
        if not refresh_token:
            raise ValueError("Refresh token is required")
        blacklist_refresh_token(refresh_token)

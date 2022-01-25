from starlette.authentication import AuthenticationBackend, AuthCredentials, SimpleUser


class AllAllowed(AuthenticationBackend):
    async def authenticate(self, conn):
        return AuthCredentials(["authenticated"]), SimpleUser("anonymous")
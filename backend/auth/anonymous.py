from starlette.authentication import (AuthCredentials, AuthenticationBackend,
                                      SimpleUser)


class AllAllowed(AuthenticationBackend):
    async def authenticate(self, conn):
        return AuthCredentials(["authenticated"]), SimpleUser("anonymous")

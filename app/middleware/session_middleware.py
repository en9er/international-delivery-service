import secrets
from datetime import datetime, timedelta

from starlette.middleware.base import BaseHTTPMiddleware


class SessionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        # Check if the user has a session ID cookie
        session_id = request.cookies.get('session_id')

        # If not, generate a new one
        if not session_id:
            # Generate a unique session ID
            session_id = secrets.token_hex(16)
            response = await call_next(request)
            cookie_expires = (
                    datetime.utcnow() + timedelta(days=365)
            ).strftime('%a, %d %b %Y %H:%M:%S GMT')
            response.set_cookie(
                key='session_id',
                value=session_id,
                expires=cookie_expires
            )

            return response

        return await call_next(request)

import time
import jwt


# JWT 处理类
class JWTAuthHandler:
    def __init__(self, secret_key: str):
        self.secret_key = secret_key

    def encode_token(self, payload: dict, expires_in: int = 3600) -> str:
        """生成带过期时间的 JWT Token"""
        payload = payload.copy()
        payload["exp"] = int(time.time()) + expires_in
        return jwt.encode(payload, self.secret_key, algorithm="HS256")

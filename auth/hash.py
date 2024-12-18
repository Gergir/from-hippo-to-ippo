import bcrypt


class Hash:
    @staticmethod
    def bcrypt(password: str) -> str:
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    @staticmethod
    def verify(plain_password: str, hashed_password: str | bytes) -> bool:
        return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())

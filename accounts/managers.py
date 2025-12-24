from django.contrib.auth.models import BaseUserManager

class UserManager(BaseUserManager):
    def create_user(self, ten_dang_nhap, password=None, vai_tro=None):
        if not ten_dang_nhap:
            raise ValueError("Phải có tên đăng nhập")

        user = self.model(
            ten_dang_nhap=ten_dang_nhap,
            vai_tro=vai_tro
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

from rest_framework import serializers
from accounts.models import User, NhanVien


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'role',
            'is_active',
            'date_joined'
        ]


class NhanVienSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = NhanVien
        fields = [
            'id',
            'user',
            'ho_ten',
            'so_dien_thoai',
            'chuc_vu',
            'luong',
            'ngay_vao_lam'
        ]

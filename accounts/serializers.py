from rest_framework import serializers
from .models import Users

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ['ten_dang_nhap', 'mat_khau']
        extra_kwargs = {
            'mat_khau': {'write_only': True}
        }

    def create(self, validated_data):
        validated_data['vai_tro'] = 'Khách hàng'
        return Users.objects.create(**validated_data)

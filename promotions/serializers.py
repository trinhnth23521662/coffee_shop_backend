# promotions/serializers.py
from rest_framework import serializers
from .models import KhuyenMai

class KhuyenMaiSerializer(serializers.ModelSerializer):
    class Meta:
        model = KhuyenMai
        fields = '__all__'

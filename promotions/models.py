# promotions/models.py
from django.db import models

class KhuyenMai(models.Model):
    LOAI_KM_CHOICES = [
        ('PHAN_TRAM', 'Phần trăm'),
        ('TIEN_MAT', 'Tiền mặt'),
    ]

    TRANG_THAI_CHOICES = [
        ('DANG_AP_DUNG', 'Đang áp dụng'),
        ('HET_HAN', 'Hết hạn'),
        ('CHUA_AP_DUNG', 'Chưa áp dụng'),
    ]

    ten_km = models.CharField(max_length=200)
    loai_km = models.CharField(max_length=20, choices=LOAI_KM_CHOICES)
    gia_tri = models.DecimalField(max_digits=10, decimal_places=2)
    dieu_kien = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    ngay_bd = models.DateTimeField()
    ngay_kt = models.DateTimeField()
    trang_thai = models.CharField(
        max_length=20,
        choices=TRANG_THAI_CHOICES,
        default='DANG_AP_DUNG'
    )

    def __str__(self):
        return self.ten_km

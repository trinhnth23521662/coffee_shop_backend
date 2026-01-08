# promotions/models.py
from django.db import models

class KhuyenMai(models.Model):
    LOAI_KM_CHOICES = [
        ('Phần trăm', 'Phần trăm'),
        ('Tiền mặt', 'Tiền mặt'),
    ]

    TRANG_THAI_CHOICES = [
        ('Đang áp dụng', 'Đang áp dụng'),
        ('Hết hạn', 'Hết hạn'),
        ('Chưa áp dụng', 'Chưa áp dụng'),
    ]

    ma_km = models.AutoField(primary_key=True)
    ten_km = models.CharField(max_length=200)
    loai_km = models.CharField(max_length=20, choices=LOAI_KM_CHOICES)
    gia_tri = models.DecimalField(max_digits=10, decimal_places=2)
    dieu_kien = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    ngay_bd = models.DateTimeField()
    ngay_kt = models.DateTimeField()
    trang_thai = models.CharField(
        max_length=20,
        choices=TRANG_THAI_CHOICES,
        default='Đang áp dụng'
    )

    class Meta:
        db_table = 'KhuyenMai'
        managed = False

    def __str__(self):
        return self.ten_km

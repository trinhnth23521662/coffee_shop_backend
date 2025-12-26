from django.db import models


class KhuyenMai(models.Model):
    ma_km = models.AutoField(primary_key=True)
    ten_km = models.CharField(max_length=200)
    loai_km = models.CharField(max_length=20)  # 'Phần trăm' hoặc 'Tiền mặt'
    gia_tri = models.DecimalField(max_digits=10, decimal_places=2)
    dieu_kien = models.DecimalField(max_digits=12, decimal_places=2, default=0)  # Đơn tối thiểu
    ngay_bd = models.DateTimeField()
    ngay_kt = models.DateTimeField()
    trang_thai = models.CharField(max_length=20, default='Đang áp dụng')  # Đang áp dụng / Hết hạn

    class Meta:
        db_table = 'KhuyenMai'
        managed = False
        app_label = 'promotions'

from django.db import models


class LoaiSP(models.Model):
    ma_loaisp = models.AutoField(primary_key=True, db_column='MaLoaiSP')
    ten_loaisp = models.CharField(max_length=150, db_column='TenLoaiSP')

    class Meta:
        db_table = 'LoaiSP'
        managed = False
        app_label = 'menu'

    def __str__(self):
        return self.ten_loaisp


class SanPham(models.Model):
    TRANG_THAI_CHOICES = [
        ('Còn', 'Còn hàng'),
        ('Hết', 'Hết hàng'),
        ('Ngừng', 'Ngừng kinh doanh'),
    ]

    ma_sp = models.AutoField(primary_key=True, db_column='ma_sp')
    ten_sp = models.CharField(max_length=200, db_column='TenSP')
    gia = models.DecimalField(max_digits=12, decimal_places=2, db_column='Gia')
    trang_thai = models.CharField(
        max_length=10,
        default='Còn',
        choices=TRANG_THAI_CHOICES,
        db_column='TrangThai'
    )
    ma_loaisp = models.ForeignKey(
        LoaiSP,
        on_delete=models.CASCADE,
        db_column='MaLoaiSP',
        related_name='san_pham'
    )

    class Meta:
        db_table = 'SanPham'
        managed = False
        app_label = 'menu'

    def __str__(self):
        return f"{self.ten_sp} - {self.get_trang_thai_display()}"

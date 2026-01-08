from django.db import models


class LoaiSP(models.Model):
    ma_loaisp = models.AutoField(primary_key=True)
    ten_loaisp = models.CharField(max_length=150)

    class Meta:
        db_table = 'LoaiSP'
        managed = False
        app_label = 'menu'


class SanPham(models.Model):
    ma_sp = models.AutoField(primary_key=True)
    ten_sp = models.CharField(max_length=200)
    gia = models.DecimalField(max_digits=12, decimal_places=2)
    trang_thai = models.CharField(max_length=10, default='Còn')
    ma_loaisp = models.ForeignKey(LoaiSP, on_delete=models.CASCADE, db_column='ma_loaisp')

    class Meta:
        db_table = 'SanPham'
        managed = False
        app_label = 'menu'
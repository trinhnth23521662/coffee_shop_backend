from django.db import models

from accounts.models import KhachHang


class DonHang(models.Model):
    ma_dh = models.AutoField(primary_key=True)
    ma_kh = models.ForeignKey(KhachHang, on_delete=models.SET_NULL, null=True, blank=True,
                              db_column='ma_kh')
    ma_ban = models.ForeignKey('tables.Ban', on_delete=models.SET_NULL, null=True, blank=True, db_column='ma_ban')
    ma_nv = models.IntegerField()
    nguon_don = models.CharField(max_length=10)
    trang_thai = models.CharField(max_length=20, default='Chờ xác nhận')
    tong_tien = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    giam_gia = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    phuong_thuc_tt = models.CharField(max_length=20)
    ngay_tao = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'DonHang'
        managed = False
        app_label = 'orders'


class ChiTietDonHang(models.Model):
    ma_ctdh = models.AutoField(primary_key=True)
    ma_dh = models.ForeignKey(DonHang, on_delete=models.CASCADE, db_column='ma_dh')
    ma_mon = models.ForeignKey('menu.SanPham', on_delete=models.CASCADE, db_column='ma_mon')
    so_luong = models.IntegerField(default=1)
    ghi_chu = models.CharField(max_length=500, null=True, blank=True)
    trang_thai_mon = models.CharField(max_length=20, default='Chờ làm')

    class Meta:
        db_table = 'ChiTietDonHang'
        managed = False
        app_label = 'orders'

from django.db import models

class LoaiSP(models.Model):
    ma_loaisp = models.AutoField(primary_key=True)
    ten_loaisp = models.CharField(max_length=150)
    
    class Meta:
        db_table = 'LoaiSP'
        managed = False

class SanPham(models.Model):
    ma_sp = models.AutoField(primary_key=True)
    ten_sp = models.CharField(max_length=200)
    gia = models.DecimalField(max_digits=12, decimal_places=2)
    trang_thai = models.CharField(max_length=10, default='Còn')
    ma_loaisp = models.ForeignKey(LoaiSP, on_delete=models.CASCADE, db_column='ma_loaisp')
    
    class Meta:
        db_table = 'SanPham'
        managed = False

class Ban(models.Model):
    ma_ban = models.AutoField(primary_key=True)
    ten_ban = models.CharField(max_length=100)
    trang_thai = models.CharField(max_length=20, default='Trống')
    
    class Meta:
        db_table = 'Ban'
        managed = False

class KhachHang(models.Model):
    ma_kh = models.AutoField(primary_key=True)
    ho_ten = models.CharField(max_length=200)
    sdt = models.CharField(max_length=20, null=True, blank=True)
    dia_chi = models.CharField(max_length=300, null=True, blank=True)
    loai_khach = models.CharField(max_length=10)
    ma_nd = models.IntegerField(null=True, blank=True)
    
    class Meta:
        db_table = 'KhachHang'
        managed = False

class DonHang(models.Model):
    ma_dh = models.AutoField(primary_key=True)
    ma_kh = models.ForeignKey(KhachHang, on_delete=models.SET_NULL, null=True, blank=True, db_column='ma_kh')
    ma_ban = models.ForeignKey(Ban, on_delete=models.SET_NULL, null=True, blank=True, db_column='ma_ban')
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

class ChiTietDonHang(models.Model):
    ma_ctdh = models.AutoField(primary_key=True)
    ma_dh = models.ForeignKey(DonHang, on_delete=models.CASCADE, db_column='ma_dh')
    ma_mon = models.ForeignKey(SanPham, on_delete=models.CASCADE, db_column='ma_mon')
    so_luong = models.IntegerField(default=1)
    ghi_chu = models.CharField(max_length=500, null=True, blank=True)
    trang_thai_mon = models.CharField(max_length=20, default='Chờ làm')
    
    class Meta:
        db_table = 'ChiTietDonHang'
        managed = False

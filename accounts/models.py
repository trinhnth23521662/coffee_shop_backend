from django.db import models

class User(models.Model):
    ma_nd = models.AutoField(primary_key=True)
    ten_dang_nhap = models.CharField(max_length=100, unique=True)
    mat_khau = models.CharField(max_length=255)
    vai_tro = models.CharField(max_length=20)

    class Meta:
        db_table = 'USERS'
        managed = False


class NhanVien(models.Model):
    ma_nv = models.AutoField(primary_key=True)
    ho_ten = models.CharField(max_length=200)
    sdt = models.CharField(max_length=20, null=True, blank=True)
    dia_chi = models.CharField(max_length=300, null=True, blank=True)
    ma_nd = models.OneToOneField(User, on_delete=models.CASCADE, db_column='ma_nd')

    class Meta:
        db_table = 'NhanVien'
        managed = False


class KhachHang(models.Model):
    TYPE_CHOICES = (
        ('online', 'online'),
        ('offline', 'offline'),
    )

    ma_kh = models.AutoField(primary_key=True)
    ho_ten = models.CharField(max_length=200)
    sdt = models.CharField(max_length=20, null=True, blank=True)
    dia_chi = models.CharField(max_length=300, null=True, blank=True)
    loai_khach = models.CharField(max_length=10, choices=TYPE_CHOICES)
    ma_nd = models.OneToOneField(User, on_delete=models.CASCADE, db_column='ma_nd', null=True, blank=True)

    class Meta:
        db_table = 'KhachHang'
        managed = False

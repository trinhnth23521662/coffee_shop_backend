from django.db import models

from accounts.models import NhanVien, KhachHang
from menu.models import SanPham
from tables.models import Ban

class DonHang(models.Model):
    ma_dh = models.AutoField(primary_key=True)

    khach_hang = models.ForeignKey(
        KhachHang,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        db_column='ma_kh'
    )

    ban = models.ForeignKey(
        Ban,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        db_column='ma_ban'
    )

    nhan_vien = models.ForeignKey(
        NhanVien,
        on_delete=models.CASCADE,
        db_column='ma_nv'
    )

    nguon_don = models.CharField(
        max_length=10,
        choices=[("online", "online"), ("offline", "offline")]
    )

    trang_thai = models.CharField(
        max_length=20,
        default="Chờ xác nhận",
        choices=[
            ("Chờ xác nhận", "Chờ xác nhận"),
            ("Đang làm", "Đang làm"),
            ("Hoàn thành", "Hoàn thành"),
            ("Hủy", "Hủy")
        ]
    )

    tong_tien = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    giam_gia = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    phuong_thuc_tt = models.CharField(
        max_length=20,
        choices=[
            ("Tiền mặt", "Tiền mặt"),
            ("Chuyển khoản", "Chuyển khoản")
        ]
    )

    ngay_tao = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'DonHang'
        managed = False

    def __str__(self):
        return f"Đơn {self.ma_dh}"

class ChiTietDonHang(models.Model):
    ma_ctdh = models.AutoField(primary_key=True)

    don_hang = models.ForeignKey(
        DonHang,
        on_delete=models.CASCADE,
        related_name='chi_tiet',
        db_column='ma_dh'
    )

    san_pham = models.ForeignKey(
        SanPham,
        on_delete=models.CASCADE,
        db_column='ma_sp'
    )

    so_luong = models.PositiveIntegerField(default=1)

    ghi_chu = models.CharField(max_length=500, blank=True)

    trang_thai_mon = models.CharField(
        max_length=20,
        default="Chờ làm",
        choices=[
            ("Chờ làm", "Chờ làm"),
            ("Đang làm", "Đang làm"),
            ("Xong", "Xong")
        ]
    )

    class Meta:
        db_table = 'ChiTietDonHang'
        managed = False

    def __str__(self):
        return f"{self.san_pham.ten_sp} x {self.so_luong}"

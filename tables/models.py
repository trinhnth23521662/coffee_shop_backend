from django.db import models

class Ban(models.Model):
    TRANG_THAI_CHOICES = [
        ('Trống', 'Trống'),
        ('Đang phục vụ', 'Đang phục vụ'),
        ('Đang dọn', 'Đang dọn'),
    ]

    ma_ban = models.AutoField(
        primary_key=True,
        db_column='ma_ban'
    )

    ten_ban = models.CharField(
        max_length=100,
        db_column='ten_ban'
    )

    trang_thai = models.CharField(
        max_length=20,
        choices=TRANG_THAI_CHOICES,
        db_column='trang_thai'
    )

    class Meta:
        db_table = 'Ban'
        managed = False

    def __str__(self):
        return f"{self.ten_ban} ({self.trang_thai})"

from django.db import models


class Ban(models.Model):
    ma_ban = models.AutoField(primary_key=True)
    ten_ban = models.CharField(max_length=100)
    trang_thai = models.CharField(max_length=20, default='Trống')

    class Meta:
        db_table = 'Ban'
        managed = False
        app_label = 'tables'

    def __str__(self):
        return f"{self.ten_ban} - {self.trang_thai}"

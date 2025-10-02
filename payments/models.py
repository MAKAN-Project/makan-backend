from django.db import models
from users.models import User

class Payment(models.Model):
    payment_id = models.AutoField(primary_key=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=45)
    method = models.CharField(max_length=45)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    paymentscol = models.CharField(max_length=45)

    class Meta:
        db_table = 'payments'

    def __str__(self):
        return f"Payment {self.payment_id}"

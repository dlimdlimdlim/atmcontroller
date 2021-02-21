from django.db import models

# Create your models here.


class BankCard(models.Model):
    user_id = models.BigIntegerField(db_index=True)
    card_number = models.BigIntegerField(unique=True)
    pin_hash = models.CharField(max_length=128)


class BankAccount(models.Model):
    user_id = models.BigIntegerField(db_index=True)
    account_name = models.CharField(max_length=256)

    class Meta:
        unique_together = [['user_id', 'account_name']]


class AccountHistory(models.Model):
    account_id = models.BigIntegerField(db_index=True)
    account_balance = models.BigIntegerField()
    last_operation = models.CharField(max_length=32)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        index_together = [['account_id', 'created_at']]


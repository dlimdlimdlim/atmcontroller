from django.db import models

from account.entity import Account, AccountRecord, Card
# Create your models here.


class BankCard(models.Model):
    user_id = models.BigIntegerField(db_index=True)
    card_number = models.BigIntegerField(unique=True)
    pin_hash = models.CharField(max_length=128)

    def to_domain(self):
        return Card(user_id=self.user_id, card_num=self.card_number, pin_salt_hash=self.pin_hash)


class BankAccount(models.Model):
    user_id = models.BigIntegerField(db_index=True)
    account_name = models.CharField(max_length=256)

    class Meta:
        unique_together = [['user_id', 'account_name']]

    def to_domain(self):
        return Account(account_id=self.id, user_id=self.user_id, name=self.account_name, histories=[])


class AccountHistory(models.Model):
    account_id = models.BigIntegerField()
    account_balance = models.BigIntegerField()
    operation = models.CharField(max_length=32)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    operation_index = models.BigIntegerField()

    class Meta:
        index_together = [['account_id', 'created_at']]
        unique_together = [['account_id', 'operation_index']]

    def to_domain(self):
        return AccountRecord(
            action=self.operation,
            balance=self.account_balance,
            time_at=self.created_at,
            record_index=self.operation_index
        )

    @staticmethod
    def from_domain(account_record: AccountRecord, account_id: int):
        AccountHistory.objects.create(
            account_id=account_id,
            operation=account_record.action,
            account_balance=account_record.balance
        )



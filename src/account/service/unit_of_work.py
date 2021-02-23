import abc

from django.db import close_old_connections, transaction

from account.adaptors.account_repo import AccountRepository, DjangoAccountRepo


class UnitOfWork(abc.ABC):
    account_data: AccountRepository

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.rollback()

    def commit(self):
        self._commit()

    @abc.abstractmethod
    def _commit(self):
        raise NotImplementedError

    @abc.abstractmethod
    def rollback(self):
        raise NotImplementedError


class DjangoUnitOfWork(UnitOfWork):
    account_data: DjangoAccountRepo

    def get_data_repo(self):
        return DjangoAccountRepo()

    def __enter__(self):
        self.account_data = self.get_data_repo()
        close_old_connections()
        transaction.set_autocommit(False)
        return super().__enter__()

    def __exit__(self, *args):
        super().__exit__(*args)
        transaction.set_autocommit(True)

    def _commit(self):
        transaction.commit()

    def rollback(self):
        transaction.rollback()
import abc

from django.db import close_old_connections, transaction

from account.adaptors.account_repo import AccountRepository, DjangoRedisAccountRepo


class AbstractUnitOfWork(abc.ABC):
    account_data: AccountRepository

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.rollback()

    def commit(self):
        self._commit()

    def collect_new_events(self):
        for item in self.account_data.seen_accounts:
            while item.new_histories:
                yield item.new_histories.pop(0)

    @abc.abstractmethod
    def _commit(self):
        raise NotImplementedError

    @abc.abstractmethod
    def rollback(self):
        raise NotImplementedError


class DjangoRedisUnitOfWork(AbstractUnitOfWork):
    account_data: DjangoRedisAccountRepo

    def get_data_repo(self):
        return DjangoRedisAccountRepo()

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
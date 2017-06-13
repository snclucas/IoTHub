import abc


class Database:
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        pass

    @abc.abstractmethod
    def get_one_by_id(self, table, doc_id):
        return

    @abc.abstractmethod
    def get_one_where(self, table, where, is_val):
        return

    @abc.abstractmethod
    def get_all(self, table):
        return

    @abc.abstractmethod
    def save(self, json_data, table):
        return

    @abc.abstractmethod
    def add_table(self, table):
        return

    @abc.abstractmethod
    def update(self, table, doc_id, doc):
        return

    @abc.abstractmethod
    def delete_all(self, table):
        return

    @abc.abstractmethod
    def delete_one(self, table, doc_id):
        return

    @abc.abstractmethod
    def delete_where(self, table, where, is_val):
        return

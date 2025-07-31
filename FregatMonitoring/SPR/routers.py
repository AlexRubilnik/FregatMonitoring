class SPRRouter:
    """Роутер для определения, какой БД пользоваться приложению, и в каких случаях"""

    def db_for_read(self, model, **hints):
        if model._meta.db_table in ('Equipment'):
            return 'SPR'

    def db_for_write(self, model, **hints):
        if model._meta.db_table in ('Equipment'):
            return 'SPR'

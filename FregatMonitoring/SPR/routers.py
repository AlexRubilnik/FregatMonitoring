class SPRRouter:
    """Роутер для определения, какой БД пользоваться приложению, и в каких случаях"""

    def db_for_read(self, model, **hints):
        if model._meta.db_table in ('Equipment','Locations','Sections','Nodes', 'Repair_operations', 'Repair_staff', 'Repair_schedule', 'Staff_positions', 'Services', 'Scheduled_operations'):
            return 'SPR'

    def db_for_write(self, model, **hints):
        if model._meta.db_table in ('Equipment','Locations','Sections','Nodes', 'Repair_operations', 'Repair_staff', 'Repair_schedule', 'Staff_positions', 'Services', 'Scheduled_operations'):
            return 'SPR'

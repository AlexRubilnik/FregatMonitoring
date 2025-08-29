from django.db import models

class Locations(models.Model): #Производственный участок
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, null=False, default='Другое')

    class Meta:
        db_table = 'Locations'


class Equipment(models.Model): #Оборудование
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, null=False, default='Другое')
    location = models.ForeignKey(Locations, on_delete=models.CASCADE, default=1)

    class Meta:
        db_table = 'Equipment'


class Sections(models.Model): #Раздел
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, null=False, default='Другое')
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, default=1) 

    class Meta:
        db_table = 'Sections'


class Nodes(models.Model): #Раздел
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, null=False, default='Другое')
    section = models.ForeignKey(Sections, on_delete=models.CASCADE, default=1) 

    class Meta:
        db_table = 'Nodes'


class Services(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, null=False, default='Другое')

    class Meta:
        verbose_name = 'Служба'
        verbose_name_plural = 'Службы'
        db_table = 'Services'


class Staff_positions(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, null=False, default='Другое')
    service = models.ForeignKey(Services, on_delete=models.CASCADE, default=1) 

    class Meta:
        verbose_name = 'Должность'
        verbose_name_plural = 'Должности'
        db_table = 'Staff_positions'


class Repair_staff(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, null=True)
    surname = models.CharField(max_length=100, null=True)
    username = models.CharField(max_length=100, null=True)
    position = models.ForeignKey(Staff_positions, null=True, on_delete=models.SET_NULL) 

    class Meta:
        verbose_name = 'Работник'
        verbose_name_plural = 'Работники'
        db_table = 'Repair_staff'


class Works(models.Model):
    id = models.AutoField(primary_key=True)
    operation_content = models.TextField()
    tools = models.TextField(null=True)
    time_min = models.IntegerField(null=True)
    staff_position= models.ForeignKey(Staff_positions, on_delete=models.CASCADE, default=1) 
    periodicity_days = models.IntegerField(null=True)
    node = models.ForeignKey(Nodes, on_delete=models.CASCADE, default=1) 
    risk = models.CharField(max_length=10, null=True)
    last_service = models.DateField(null=True)
    next_service = models.DateField(null=True)

    class Meta:
        db_table = 'Repair_operations'

        
class Repair_schedule(models.Model):
    operation = models.OneToOneField(Works, primary_key=True, on_delete=models.CASCADE, default=1)
    for i in range(1, 53):
        exec(f"_{i} = models.IntegerField(null=False, default=0)")


    class Meta:
        db_table = 'Repair_schedule'


class Repair_schedule_fact(models.Model):
    operation = models.OneToOneField(Works, primary_key=True, on_delete=models.CASCADE, default=1)
    for i in range(1, 53):
        exec(f"_{i} = models.IntegerField(null=False, default=0)")


    class Meta:
        db_table = 'Fact_repair_schedule'


class Scheduled_operations(models.Model):
   id = models.AutoField(primary_key=True)
   operation = models.ForeignKey(Works, on_delete=models.CASCADE)
   start_date = models.DateField(null=True)
   finish_date = models.DateField(null=True)
   staff = models.ForeignKey(Repair_staff, null=True, on_delete=models.DO_NOTHING) 
   current_status = models.IntegerField(null=False, default=0)
   comment = models.TextField(null=True)
   elapsed_time_min = models.IntegerField(null=True)
   start_timestamp = models.DateTimeField(null=True)
   finish_timestamp = models.DateTimeField(null=True)

   class Meta:
        db_table = 'Scheduled_operations'

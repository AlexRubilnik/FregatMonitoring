from django.contrib import admin
from django import forms

from .models import Services, Staff_positions, Repair_staff
# Register your models here.

class Staff_positionsInline(admin.TabularInline):
    model = Staff_positions
    can_delete = True
    show_change_link = True
    extra=0

class ServicesAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    readonly_fields = []
    inlines = [Staff_positionsInline] 

class Repair_staffInline(admin.TabularInline):
    model = Repair_staff
    can_delete = True
    show_change_link = True
    extra=0

class Staff_positionsAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'service_name']
    inlines = [Repair_staffInline] 

    @admin.display(ordering="service__name")
    def service_name(self, obj):
        return obj.service.name

class CustomModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
         return "%s  Служба:%s" % (obj.name, obj.service.name)

class Repair_staffAdminForm(forms.ModelForm):
    position = CustomModelChoiceField(queryset=Staff_positions.objects.all())

    class Meta:
        model = Repair_staff
        fields = '__all__'

class Repair_staffAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'surname', 'username', 'position_name', 'position_service']
    form = Repair_staffAdminForm

    @admin.display()
    def position_name(self, obj):
        try:
            return obj.position.name
        except:
            return ""

    @admin.display()
    def position_service(self, obj):
        try:
            return obj.position.service.name
        except:
            return ""

admin.site.register(Services, ServicesAdmin)
admin.site.register(Staff_positions, Staff_positionsAdmin)
admin.site.register(Repair_staff, Repair_staffAdmin)
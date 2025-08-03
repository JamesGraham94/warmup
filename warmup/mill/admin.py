from django.contrib import admin
from .models import Mill, Program
# Register your models here.

@admin.register(Mill)
class MillAdmin(admin.ModelAdmin):

    list_display = ['machine_name','x_limits','y_limits','z_limits']

@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):

    list_display = ['program_name','code']





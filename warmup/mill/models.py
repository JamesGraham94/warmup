from django.db import models
from django.urls import reverse

# Create your models here.

class Mill(models.Model):
    asset_number = models.CharField(max_length=5, db_index=True, blank=True, null=True)
    machine_name = models.CharField(max_length=5, db_index=True, blank=True, null=True)
    x_limits = models.CharField(max_length=5, db_index=True, blank=True, null=True)
    y_limits = models.CharField(max_length=5, db_index=True, blank=True, null=True)
    z_limits = models.CharField(max_length=5, db_index=True, blank=True, null=True)
    g54_x = models.CharField(max_length=5, db_index=True, blank=True, null=True)
    g54_y = models.CharField(max_length=5, db_index=True, blank=True, null=True)
    g54_z = models.CharField(max_length=5, db_index=True, blank=True, null=True)
    feed_start  = models.CharField(max_length=50, db_index=True, blank=True, null=True)
    feed_end    = models.CharField(max_length=50, db_index=True, blank=True, null=True)
    rpm_start   = models.CharField(max_length=50, db_index=True, blank=True, null=True)
    rpm_end     = models.CharField(max_length=50, db_index=True, blank=True, null=True)
    tool_lenght = models.CharField(max_length=50, db_index=True, blank=True, null=True)
    coolant     = models.BooleanField(default=True, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated = models.DateTimeField(auto_now=True, blank=True, null=True)
    owner = models.CharField(max_length=50, db_index=True, blank=True, null=True)



    def __str__(self):
        return self.machine_name
    
    def get_absolute_url(self):
        return reverse('form', args={self.pk})


class Program(models.Model):
    program_name = models.CharField(max_length=15, db_index=True, blank=True, null=True)
    code = models.TextField(max_length=3000, db_index=True, blank=True, null=True)
   
    def __str__(self):
        return self.program_name


    
    
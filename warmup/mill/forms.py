from django import forms
from .models import Mill

class MillCreateForm(forms.ModelForm):
	class Meta:
		model = Mill
		fields = '__all__'

class UpdateForm(forms.ModelForm):
	class Meta:
		model = Mill
		fields = ["feed_start","feed_end","rpm_start","rpm_end","coolant"]
		#fields="__all__"
from django.shortcuts import render,get_object_or_404
from django.contrib import messages

from django.views.generic.edit import UpdateView
from .models import Mill, Program
from .forms import UpdateForm
from django.urls import reverse_lazy


#https://www.w3schools.com/python/python_strings_format.asp

# Create your views here.
def home(request):
	#function that queries all mills and display the context
	mills = Mill.objects.all()
	context = {'mills':mills}
	
	return render(request,'home.html',context)


class UpdateFormView(UpdateView):
	#Generic form to update parameters
	template_name="form.html"
	form_class = UpdateForm
	model= Mill
	success_url = reverse_lazy('home')


def fanuc(request,pk):

	id=pk
	mills = Mill.objects.filter(id=pk)
	mills_instance = Mill.objects.get(id=pk)
	obj = get_object_or_404(Mill,id=pk)

	feed_start = mills_instance.feed_start 
	feed_end = mills_instance.feed_end 
	rpm_start = mills_instance.rpm_start 
	rpm_end = mills_instance.rpm_end 

	x_limits = mills_instance.x_limits
	y_limits = mills_instance.y_limits
	z_limits = mills_instance.z_limits

	coolant = mills_instance.coolant

	if coolant :
		m8 = "M8"
	else:
		m8= "" 


	
	program = f"""
			O8000;
			(Local Variables Initialization)
			#1=0; initialized  counter Incremental Feed
			#9 =  {feed_start}; Feed Start
			#10 = {feed_end} ; Feed End
			#2=0; initialized  counter Incremental Speed
			#11 = {rpm_start}; Spindle Start
			#12 = {rpm_start}; Spindle End
			#24=  {x_limits}; X axis
			#25=  {y_limits}; Y axis
			#26=- {z_limits}; Z axis
			#5021 = 50; G54 x axis
			#5022 = 50; G54 y axis
			#5023 = 50; G54 z axis
			#11001 =75; Tool length 1 geometric compesantion
			G10 L2 P1. X#5021 Y#5022 Z#5023 ; Set values G54 XYZ
			G21 G90 G40 G49 G80 (Metric, Absolute, Cutter Comp Cancel, Tool Length Comp Cancel, Canned Cycle Cancel)
			(G10.6 Z5)
			G91 G28 Z0.0 (Return Z to home position)
			N30 G91 G28 X0.0 Y0.0 (Return X and Y to home position)
			T1 M06 (Tool change to Tool 1)
			G43 H#11001 Z0.1 
			{m8}
			WHILE [#11 LE #12] DO 1
  			S#11 M03 (SET SPINDLE SPEED AND START)
  			G04 P1000 (DWELL FOR 1 SECOND)
  			#2 = #2 + 500 (INCREMENT SPINDLE SPEED)
			END 1
			WHILE [#1 LT #10 ] DO 2;[Outer Loop]
			G01 G91 X#24. Y#25 Z#26  F#9+#1. M3 S#11;(travel limit)
			X-#24. Y-#25  Z-#26
			#1=#1+10
			END 2;[Outer Loop]
			M5
			M30
			"""
	
	
	
	context={ 'id':id,'mills':mills,'obj':obj, 'feed_start':feed_start,
			  'feed_end':feed_end, 'rpm_start':rpm_start,'rpm_end':rpm_end, 
			  'x_limits':x_limits,'y_limits':y_limits,'z_limits':y_limits,
			  'coolant':coolant, 'm8':m8,	
		      'program':program,
			}
	
	return render(request,'fanuc.html',context)
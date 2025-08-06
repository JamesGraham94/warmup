from django.shortcuts import render,get_object_or_404
from django.contrib import messages

from django.views.generic.edit import UpdateView
from .models import Mill, Program
from .forms import UpdateForm
from django.urls import reverse_lazy




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
	# Function that queries database and create Gcode for Fanuc control  by python string with embed variables from database
	id=pk
	mills = Mill.objects.filter(id=pk)
	mills_instance = Mill.objects.get(id=pk)
	obj = get_object_or_404(Mill,id=pk)

	# get Values from queried object instance
	feed_start = mills_instance.feed_start 
	feed_end = mills_instance.feed_end 
	rpm_start = mills_instance.rpm_start 
	rpm_end = mills_instance.rpm_end 

	x_limits = mills_instance.x_limits
	y_limits = mills_instance.y_limits
	z_limits = mills_instance.z_limits

	coolant = mills_instance.coolant

	# conditions to that checks if coolant is True or not.
	if coolant :
		m8 = "M8"
		m9 = "M9"
	else:
		m8 = "" 
		m9 = ""


	
	program = f"""
			O8000;
			(Local Variables Initialization)
			#1=0; initialized  counter Incremental Feed
			#9 =  {feed_start}; Feed Start
			#10 = {feed_end} ; Feed End
			#2=0; initialized  counter Incremental Speed
			#11 = {rpm_start}; Spindle Start
			#12 = {rpm_end}; Spindle End
			#24=  {x_limits}; X axis
			#25=  {y_limits}; Y axis
			#26=- {z_limits}; Z axis
			#5021 = 50; G54 X axis
			#5022 = 50; G54 Y axis
			#5023 = 50; G54 Z axis
			#11001 =75; Tool length 1 geometric compesantion
			G10 L2 P1. X#5021 Y#5022 Z#5023 ; Set values G54 XYZ
			G21 G90 G40 G49 G80 (Metric, Absolute, Cutter Comp Cancel, Tool Length Comp Cancel, Canned Cycle Cancel)
			(G10.6 Z5)
			G91 G28 Z0.0 (Return Z to home position)
			N30  G28 X0.0 Y0.0 (Return X and Y to home position)
			T1 M06 (Tool change to Tool 1)
			G43 H#11001 Z0.1 
			{m8}
			WHILE [#11 LE #12] DO 1
  			S#11 + #2 M03 (SET SPINDLE SPEED AND START)
  			G04 P1000 (DWELL FOR 1 SECOND)
  			#2 = #2 + 500 (INCREMENT SPINDLE SPEED)
			END 1
			WHILE [#1 LT #10 ] DO 2;[Outer Loop]
			G01  X#24. Y#25 Z#26  F#9+#1. M3 S#11;(travel limit)
			X-#24. Y-#25  Z-#26
			#1=#1+10
			END 2;[Outer Loop]
			{m9}
			M5
			M30
			"""
	
	
	
	context={ 'id':id,'mills':mills,'obj':obj, 'feed_start':feed_start,
			  'feed_end':feed_end, 'rpm_start':rpm_start,'rpm_end':rpm_end, 
			  'x_limits':x_limits,'y_limits':y_limits,'z_limits':y_limits,
			  'coolant':coolant, 'm8':m8, 'm9':m9,
		      'program':program,
			}
	
	return render(request,'fanuc.html',context)


def heidenhain(request,pk):
	# Function that queries database and create Gcode for heidenhain control  by python string with embed variables from database
	id=pk
	mills = Mill.objects.filter(id=pk)
	mills_instance = Mill.objects.get(id=pk)
	obj = get_object_or_404(Mill,id=pk)

	# get Values from queried object instance
	feed_start = mills_instance.feed_start
	feed_end = mills_instance.feed_end
	rpm_start = mills_instance.rpm_start
	rpm_end = mills_instance.rpm_end

	x_limits = mills_instance.x_limits
	y_limits = mills_instance.y_limits
	z_limits = mills_instance.z_limits

	coolant = mills_instance.coolant

	# conditions to that checks if coolant is True or not.
	if coolant :
		m8 = "M8"
		m9 = "M9"
	else:
		m8=  "  "
		m9 = "  "



	program = f"""
			O8000;
			BEGIN PGM WARMUP MM
            BLK FORM 0.1 Z X+{x_limits} Y+{y_limits} Z+{z_limits} ; Define virtual machine envelope for simulation User Defined Limits
            

            ; Define variables for warm-up parameters
            FN 1: Q1 = {rpm_start} ; Initial spindle speed (RPM) USER Defined
            FN 1: Q2 = {rpm_end} ; Maximum spindle speed (RPM) USER Defined
            FN 1: Q3 = 100 ; Spindle speed increment (RPM)
            FN 1: Q4 = {feed_start} ; Axis feed rate (mm/min)  USER Defined
            FN 1: Q10 ={feed_end} ; Axis feed rate (mm/min) USER Defined
            FN 1: Q11 = 10; Feed Rate increment (mm/min)
            FN 1: Q5 = 1000 ; Max axis travel (mm) - Adjusted for machine size
            FN 1: Q6 = 50 ; Axis travel increment (mm)
            FN 1: Q7 = {x_limits} ;Axis Travel limit X (mm) USER Defined
            FN 1: Q8 = {y_limits} ;Axis Travel limit y (mm) USER Defined
            FN 1: Q9 = {z_limits} ;Axis Travel limit z (mm) USER Defined
			FN 1: Q12 = TBD ; G54 X
            FN 1: Q13 = TBD ; G54 Y
            FN 1: Q14 = TBD ; G54 Z
			FN 1: Q114 = 100 ; Active tool lenght

			G54 X=Q12 Y=Q13 Z=Q14  ; Applies the values of Q10, Q11, and Q12 to the G54 work offset
            TOOL CALL 1 Z S5000 DL+Q114 ; Call a dummy tool, set initial spindle speed


            ; Spindle warm-up cycle
            LBL 1
            FN 0: Q1 = Q1 + Q3 ; Increment spindle speed
            S Q1 M3; Set new spindle speed
            DWELL 0.5 ; Dwell for 0.5 seconds
            FN 2: IF Q1 LT Q2 GOTO LBL 1 ; Loop until max speed is reached
            S Q2 M3; Maintain max speed for a period
            DWELL 60 ; Dwell for 60 seconds at max speed
            S 0 ; Stop spindle

            ; Axis warm-up cycle
            LBL 2
            FN 0: Q4 = Q4 + Q11 ; Set axis feed rate
			S Q1 M3; Set spindle Speed

            ; X-axis movement
            {m8} ; Turn on Coolant User Defined
            LX +Q7 FQ4 ; Move X to positive limit
            LX -Q7 FQ4 ; Move X to negative limit
            {m9} ; User Defined


            ; Y-axis movement
            {m8} ; Turn on Coolant User Defined
            LY +Q8 FQ4 ; Move Y to positive limit
            LY -Q8 FQ4 ; Move Y to negative limit
            {m9} ; turn on Coolant User Defined


            ; Z-axis movement
            {m8} ; Turn on Coolant User Defined
            LZ +Q9 FQ4 ; Move Z to positive limit
            LZ -Q9 FQ4 ; Move Z to negative limit
            {m9} ; turn on Coolant User Defined
            FN 2: IF Q4 LT Q10 GOTO LBL 2 ; Loop until Max Feed Rate is Reached

            ; Return to home position
            L Z+0 R0 FMAX ; Rapid Z to home
            L X+0 Y+0 R0 FMAX ; Rapid X and Y to home

            END PGM WARMUP MM
			"""



	context={ 'id':id,'mills':mills,'obj':obj, 'feed_start':feed_start,
			  'feed_end':feed_end, 'rpm_start':rpm_start,'rpm_end':rpm_end,
			  'x_limits':x_limits,'y_limits':y_limits,'z_limits':y_limits,
			  'coolant':coolant, 'm8':m8, 'm9':m9,
		      'program':program,
			}

	return render(request,'heidenhain.html',context)
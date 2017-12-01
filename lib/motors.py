'''
	@desc 			Motor Directions and Defaults.
					Turn Servos 0 - 180 __ Middle pos = 90
					Thrusters   1100 to 1900 Stopped = 1500 
	@createdBy 		Juan Carlos Aguilera jcjc@gmail.com
	@created_at 	2017-06-05 Settings for RoboBoat competition
	@updatedBy		Marcopolo Gil Melchor		 
	@updated_at 	2017-11-28 Restructuration and comments. 
'''

import sys
import time
import serial
import serial.tools.list_ports as ports

class Motors:
	def __init__(self):
		self.previousRightMotorValue = 0;
		self.previousLeftMotorValue = 0;

		self.minRotationS = 300 #rev/min
		self.maxRotationS = 300 #rev/min

		self.maxPowerValue = 1900;
		self.minPowerValue = 1100;

		self.powerR = 0 ; 
		self.powerL = 0 ;

		self.thrusterInitPosition = 1500
		self.thrustersBack  = 'b'
		self.thrustersFront = 'f'
		self.servoInitPosition = 90;
		self.baudRate = 115200;

		#serial communication Hanlder
		ser = serial.Serial(self.get_port(), baudRate );

	'''
	@desc 	Get imu port **
	@params None
	@return string
	'''
	def get_port(self):
		pts = list(ports.comports());

		if not pts:
			sys.exit('Motors Arduino not found');
		else:
			for p in pts:
				if (p[1].find('ACM') == 3):
					return p[0];
				elif (p[1].find('Serial') == 7):
					return p[0];
				elif (p[1].find('USB2.0-Serial') == 0) :
					return p[0];
				elif (p[1].find('USB2.0-Serial') == 0) :

			sys.exit('Motors Arduino not found');

	#format value to proper length
	'''
	@desc 	format value to proper length
	@params string
	@return string
	'''
	def check_value_size(val):
		if(len(val) == 4):
			return val ;
		elif(len(val) == 3):
			return '0' + val ;
		elif(len(val) == 2):
			return '00' + val ;
		elif(len(val) == 1):
			return '000' + val ;

	'''
	@desc 	move thrusters **
	@params 
			int powerR power value for right thruster. It must be inside the PWM lectures.
			int powerL  power value for left thruster. It must be inside the PWM lectures.
	@return string
	'''
	def move_thrusters(powerR=1500, powerL=1500):
		#validate the pwm range
		if(powerR < 1100 or powerR > 1900 or powerL < 1100 or powerL > 1900):
			print("Thruster power must be between 1100 - 1900");
		else:
			#Format motors value
			pR = str(powerR);
			pR = self.check_value_size(pR);
			pL = str(powerL);
			pL = self.check_value_size(pL);
			val = '%' + 'B,' + pR + ',' + pL + '%';

			#Send motors value to arduino
			self.ser.write(val.encode());
			self.ser.flush();

			#Debug response
			print(self.ser.read(self.ser.inWaiting()).decode());

	def move(powerR=0,powerL=0):
		#validate the pwm range
		if(powerR < -400 or powerR > 400 or powerL < -400 or powerL > 400):
			print("The power is not on the correct range");
		else:
			realPowerValueR = round(powerR + 1500);
			realPowerValueL = round(powerL + 1500);
			
			self.move_thrusters(realPowerValueR,realPowerValueL);
			#while(utility.previousLeftMotorValue != powerL or utility.previousRightMotorValue != powerR):
			#	checkDifference(powerR, powerL);

	#Send gradual changes to motors
	def checkDifference(currPowerR, currPowerL):
		threshold = 0.025 * (maxPowerValue - minPowerValue );

		#Get the difference between the current power and the last one
		diffL = abs(currPowerL - self.previousLeftMotorValue);
		diffR = abs(currPowerR - self.previousRightMotorValue);

		#Check were the direction is going
		# 1 = Increase Power
		#-1 = Decrease Power
		if(diffL != 0): 
			directionL = (currPowerL - self.previousLeftMotorValue)  / diffL ;
		else:
			directionL = 0;
		if(diffR != 0): 
			directionR = (currPowerR - self.previousRightMotorValue) / diffR ;
		else:
			directionR = 0;

		if(diffR > threshold and diffL > threshold ):
			#Increase Right Motor Power
			if(directionR > 0):
				self.previousRightMotorValue += threshold;
			#Decrease Right Motor Power
			elif(directionR < 0):
				self.previousRightMotorValue -= threshold;
			
			#Increase Left Motor Power
			if(directionL > 0):
			self.previousLeftMotorValue += threshold;
		#Decrease Left Motor Power
		elif(directionL < 0):
			self.previousLeftMotorValue -= threshold;

		realPR = int(self.previousRightMotorValue)+int(thrusterInitPosition);
		realPL = int(self.previousLeftMotorValue) +int(thrusterInitPosition);
		
		#print(realPR,realPL);
		self.move_thrusters(realPR,realPL);
		time.sleep(0.125);
			
	elif(diffR > threshold and diffL < threshold):
		if(directionR > 0):
			self.previousRightMotorValue += threshold;
		#Increase
		elif(directionR < 0):
			self.previousRightMotorValue -= threshold;

		self.previousLeftMotorValue = currPowerL;

		realPR = int(self.previousRightMotorValue)+int(thrusterInitPosition);
		realPL = int(self.previousLeftMotorValue) +int(thrusterInitPosition);
		
		#print(realPR,realPL);
		self.move_thrusters(realPR,realPL);
		time.sleep(0.125);
		
	elif(diffR < threshold and diffL > threshold):
		#Increase
		if(directionL > 0):
			self.previousLeftMotorValue += threshold;
		#Decrease
		elif(directionL < 0):
			self.previousLeftMotorValue -= threshold;

		realPR = int(self.previousRightMotorValue)+int(thrusterInitPosition);
		realPL = int(self.previousLeftMotorValue) +int(thrusterInitPosition);
		
		#print(realPR,realPL);
		self.move_thrusters(realPR,realPL);
		time.sleep(0.125);
	else:
		self.previousLeftMotorValue  = currPowerL;
		self.previousRightMotorValue = currPowerR;
		
		realPR = int(self.previousRightMotorValue)+int(thrusterInitPosition);
		realPL = int(self.previousLeftMotorValue) +int(thrusterInitPosition);

		#print(realPR,realPL);
		self.move_thrusters(realPR,realPL);
		time.sleep(0.125);

'''
	@name       	imu.py
    @desc 			Imu Controller.
					This file has all the necesary functions to access the imu for the
					autonomous navigation, such as position, orientation, velocity,
					acceleration, etc.
	@author 		Marcopolo Gil Melchor marcogil93@gmail.com
	@created_at 	2017-06-08 
	@updated_at 	2017-11-28 Restructuration and comments. 
	@dependecies	python3
'''

'''
	Required dependencies
'''
#Vector Nav library
import os
import sys
sys.path.append('/usr/local/lib/python3.4/dist-packages/vnpy')
from vnpy import *

#Basic libraries
import math
import time

#Debug libraries
from inspect import getmembers
from pprint import pprint

#	CONSTANTS
EARTH_RADIUOS = 6371000;

'''
@desc 	Init imu module connection **
@params None
@return None
'''

class Imu:
	def __init__(self):
		self.northYaw = 0;
		self.earthRadious = EARTH_RADIUOS;
		self.vnSensor = VnSensor();
		self.baudRate = 115200;
		self.vnSensor.connect(self.get_port(), self.baudRate);

	'''
	@desc 	Get imu port **
	@params None
	@return string
	'''
	def get_port(self):
		pts = list(ports.comports());

		if not pts:
			sys.exit('Imu not found');
		else:
			for p in pts:
				if (p[1].find('USB-RS232') == 0) :
					return = p[0];

			sys.exit('Imu not found');

	'''
	@desc 	Get Imu model information **
	@params None
	@return string
	'''
	def print_model(self):
		return self.vnSensor.read_model_number(self);

	'''
	@desc 	Get  number of listening Satellites**
	@params None
	@return integer 
	'''
	def get_num_satellites(self):
		#Return values of gps
		#'gps_fix', 'lla', 'ned_acc', 'ned_vel', 'num_sats', 'speed_acc', 'this', 'time', 'time_acc', 'week'
		return self.vnSensor.read_gps_solution_lla(self).num_sats;

	'''
	@desc 	Get averages of latitude and longitud coords after 10 tests
	@params None
	@return dynamic array
				float longitud
				float latitude
	'''
	def get_gps_coords(self):
		coord_x = 0;
		coord_y = 0;

		#Get average coords of 10 tests
		for i in range(10):
			lla = self.vnSensor.read_gps_solution_lla(self);
			coord_x += lla.lla.x;
			coord_y += lla.lla.y;
		
		coord_x = coord_x / 10;
		coord_y = coord_y / 10;

		coords = {
			'latitude': coord_x,
			'longitud': coord_y,
		}

		return coords;

	'''
	@desc 	Get  yaw pitch roll degrees
	@params None
	@return vec3f object
				float x 
				float y
				float z 
	'''
	def get_yaw_pitch_roll(self):
		return self.vnSensor.read_yaw_pitch_roll(self);

	'''
	@desc 	Get  yaw degree
	@params None
	@return float degree
	'''
	def get_yaw_orientation(self):
		degree = self.vnSensor.read_yaw_pitch_roll(self).x%360;

		if(degree > 180):
			degree = degree - 360;

		return degree;

	'''
	@desc 	Get  magnetic fields measurements
	@params None
	@return vec3f object of cgs (centimetre–gram–second) units (Gaussian units)
				float x 
				float y
				float z 
	'''
	def get_magnetic_measurments(self):
		return self.vnSensor.read_magnetic_measurements(self);

	'''
	@desc 	Get  magnetic fields measurements
	@params None
	@return ???
	'''
	def get_magnetic_and_gravity_reference(self):
		return self.vnSensor.read_magnetic_and_gravity_reference_vectors(self);

	'''
	@desc 	Get  all imu measurments
	@params None
	@return ???
	'''
	def get_imu_measurements(self):
		return self.vnSensor.read_imu_measurements(self);

	'''
	@desc 	Get acceleration and velocity vectors
	@params None
	@return dynamic array
				vec3f acceleration
				vec3f velocity
	'''
	def get_gps_acceleration_velocity(self):
		lla = self.vnSensor.read_gps_solution_lla(self);

		return {
			'acceleration': lla.ned_acc,
			'velocity': lla.ned_vel
		}

	'''
	@desc Get acceleration and velocity vectors
	@params None
	@return dynamic array
				vec3f acceleration
				vec3f velocity
	'''
	def get_angular_rates(self):
		angles = self.vnSensor.read_angular_rate_measurements(self);

		return {
			'x': angles.x%360,
			'y': angles.y%360,
			'z': angles.z%360,
		}

	'''
	@desc Get acceleration
	@params None
	@return vec3f acceleration
	'''
	def get_acceleration(self):
		return self.vnSensor.read_acceleration_measurements(self);

	'''
	@desc Get delta theta
	@params None
	@return dynamic array
				x
				y
				z
	'''
	def get_delta_theta(self):
		angles = self.vnSensor.read_delta_theta_and_delta_velocity(self).delta_theta;

		return {
			'x': angles.x%360,
			'y': angles.y%360,
			'z': angles.z%360,
		}

	'''
	@desc Get delta velocity
	@params None
	@return vec3f velocity
	'''
	def get_delta_velocity(self):
		return self.vnSensor.read_delta_theta_and_delta_velocity(self).delta_velocity;

	'''
	@desc Get needed degrees to point north
	@params None
	@return float degree
	'''
	def get_degrees_to_north_orientation(self):
		degree = (self.get_yaw_orientation(self)%360) - self.northYaw;

		if (degree > 180):
			degree = degree - 360;

		return degree;

	'''
	@desc get degrees and distance to gps coords
	@params goal latitude and longitud
	@return dynamic array
				float distance  meters
				float degrees 
	'''
	def get_degrees_and_distance_to_gps_coords(latitude2, longitud2):
		north = (self.get_yaw_orientation(self)%360) - self.northYaw;

		if (north > 180):
			north = north - 360;

		coords = self.get_gps_coords(self);
		latitude1 = coords['latitude'];
		longitud1 = coords['longitud'];

		#print(coords);
		#print(latitude2, longitud2);

		longitud_distance = (longitud1 - longitud2);
		y_distance = math.sin(longitud_distance) * math.cos(latitude2);
		x_distance = math.cos(latitude1) * math.sin(latitude2) - math.sin(latitude1) * math.cos(latitude2) * math.cos(longitud_distance);
		bearing = math.atan2(y_distance, x_distance);
		bearing = math.degrees(bearing) - north;
		bearing = (bearing + 360) % 360;

		if (bearing > 180):
			bearing = bearing - 360;

		phi1 = math.radians(latitude1);
		phi2 = math.radians(latitude2);
		dphi = math.radians(latitude2 - latitude1);
		dlam = math.radians(longitud2 - longitud1);
		a = math.sin(dphi/2)*math.sin(dphi/2) + math.cos(phi1)*math.cos(phi2)* math.sin(dlam/2)*math.sin(dlam/2);
		c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a));
		distance = self.earthRadious * c;

		return {
			'distance': int(distance),
			'degree': int(bearing) * -1
		}

	'''
	@desc test of compass
	@params None
	@return None
	'''
	def compass(self):
		last_magnetic_x = self.vnSensor.read_magnetic_measurements(self).x;
		direction = 0;
		
		while True:
			magnetics = self.vnSensor.read_magnetic_measurements(self);
			
			#print(magnetics);
			
			if(magnetics.y > 0):
				direction = 90 - math.atan(magnetics.x/magnetics.y)*180 / math.pi
			elif(magnetics.y < 0):
				direction = 270 - math.atan(magnetics.x/magnetics.y)*180 / math.pi
			else:
				if(magnetics < 0):
					direction = 180;
				else:
					direction = 0;
			
			if(direction > 180):
				direction -= 360;
				
			
			print(direction + 30);
			print(magnetics.x);
			'''		if(magnetics.x - last_magnetic_x > 0):

				print("bien");
			else:
				print("mal");

			last_magnetic_x = magnetics.x;'''
			time.sleep(.100);

	'''
	@desc test of compass
	@params None
	@return None
	'''
	def compass2(self):
		last_magnetic_x = self.vnSensor.read_magnetic_measurements(self).x;
		direction = 1;

		while True:
			magnetics = self.vnSensor.read_magnetic_measurements(self);
			
			#print(magnetics);
			
			if(magnetics.y > 0):
				direction = 90 - math.atan(magnetics.x/magnetics.y)*180 / math.pi
			elif(magnetics.y < 0):
				direction = 270 - math.atan(magnetics.x/magnetics.y)*180 / math.pi
			else:
				if(magnetics < 0):
					direction = 180;
				else:
					direction = 0;
			
			if(direction > 180):
				direction -= 360;
				
			
			print(direction + 30);

			if(magnetics.x - last_magnetic_x > 0):

				print("bien");
			else:
				print("mal");

			last_magnetic_x = magnetics.x;
			time.sleep(.100);
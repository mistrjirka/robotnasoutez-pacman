from ev3dev2.sensor import GyroSensor
from ev3dev2.motor import LargeMotor
from time import sleep
import math
from timeit import default_timer as timer

class TrueTurn:
	def __init__(self, motor1Port, motor2Port, gyroPort=None, wheelDiameter=None): #init
		if GyroSensor != None:
			self.GS = GyroSensor(gyroPort)
		else:
			self.GS = GyroSensor()
		self.M1 = LargeMotor(motor1Port)
		self.M2 = LargeMotor(motor2Port)
		self.motor_stop = True
		self.wheelDiameter = wheelDiameter
		self.time = 0
		self.MDistanceRunning = True
		self.distance = 0
		self.pauseDistance = []
		self.GS.mode = 'GYRO-ANG'
		
	def turn(self, degrees, speed = 150, tolerance = 0.05):
		self.stopMotors()
		self.tolerance = tolerance
		self.speed = speed
		multiplier = -1
		if degrees > 0:
			multiplier = 1
		
		self.resetValue()
		#~ self.GS.mode = 'GYRO-ANG'
		
		angle = self.GS.value()
		running = False
		self.breaker = False
		
		rightTurn = False # not actually right
		
		leftTurn = False # not actually left
		
		slowRightTurn = False # not actually right
		
		slowLeftTurn = False # not actually left
		if tolerance > 0:
			field = range(math.ceil(degrees - self.tolerance * degrees), math.ceil(degrees + self.tolerance * degrees), multiplier)
			advancedField = range(math.ceil(degrees - 0.1 * degrees), math.ceil(degrees + 0.1 * degrees), multiplier)
			print (advancedField)
		else:
			field = [self.tolerance]
			advancedField = range(math.ceil(degrees - 0.1 * degrees), math.ceil(degrees + 0.1 * degrees), multiplier)
			print (advancedField)
		
		while self.GS.value() - angle not in field:
			print (advancedField)
			print (self.GS.value() - angle)
			print(abs(self.GS.value() - angle))
			if self.GS.value() - angle in advancedField:
				#~ print("minor")
				print(self.GS.value())
				if abs(self.GS.value() - angle) <  abs(field[0]): #we have to make them absolute because we want to turn on both sides
					if not slowRightTurn:
						#~ print("slow right")
						self.M1.run_forever(speed_sp=self.speed * multiplier / 2.5)
						self.M2.run_forever(speed_sp=self.speed * multiplier * -1 /2.5)
						slowRightTurn = True
						slowLeftTurn = False
						sleep(0.001)
				
				if abs(self.GS.value() - angle) > abs(field[len(field) - 1]): #we have to make them absolute because we want to turn on both sides
					if not leftTurn:
						#~ print("slow right")
						self.M1.run_forever(speed_sp=self.speed * multiplier * -1 / 2)
						self.M2.run_forever(speed_sp=self.speed * multiplier / 2)
						slowRightTurn = False
						slowLeftTurn = True
						sleep(0.001)
			
			else:
				if abs(self.GS.value() - angle) <  abs(field[0]): #we have to make them absolute because we want to turn on both sides
					if not rightTurn:
						#~ print("normal")
						print(self.GS.value())
						self.M1.run_forever(speed_sp=self.speed * multiplier)
						self.M2.run_forever(speed_sp=self.speed * multiplier * -1)
						rightTurn = True
						leftTurn = False
					else:
						sleep(0.0012)
				
				if abs(self.GS.value() - angle) > abs(field[len(field) - 1]): #we have to make them absolute because we want to turn on both sides
					if not leftTurn:
						print(self.GS.value())
						#~ print("normal left")
						self.M1.run_forever(speed_sp=self.speed * multiplier * -1)
						self.M2.run_forever(speed_sp=self.speed * multiplier)
						rightTurn = False
						leftTurn = True
					else:
						sleep(0.0012)
		self.M1.stop()
		self.M2.stop()
		sleep(0.1)
		print("ok it works")
		leftTurn = False
		rightTurn = False
		slowLeftTurn = False
		slowRightTurn = False
		
		if self.GS.value() - angle not in field:
			while self.GS.value() - angle not in field:
				if abs(self.GS.value() - angle) <  abs(field[0]): #we have to make them absolute because we won to turn on both sides
					if not rightTurn:
						print(self.GS.value() - angle)
						#~ print ("micro")
						self.M1.run_forever(speed_sp=self.speed * multiplier / 5)
						self.M2.run_forever(speed_sp=self.speed * multiplier * -1 /5)
						rightTurn = True
						leftTurn = False
						sleep(0.001)
				
				if abs(self.GS.value() - angle) > abs(field[len(field) - 1]): #we have to make them absolute because we won to turn on both sides
					if not leftTurn:
						print(self.GS.value() - angle)
						#~ print("working")
						self.M1.run_forever(speed_sp=self.speed * multiplier * -1 / 5)
						self.M2.run_forever(speed_sp=self.speed * multiplier / 5)
						rightTurn = False
						leftTurn = True
						sleep(0.001)
			self.M1.stop()
			self.M2.stop()
		self.resetValue()
		return True
	def straight(self, direction, speed, tolerance):
		self.stopMotors()
		self.resetValue()
		#~ self.GS.mode = 'GYRO-ANG'
		angle = self.GS.value()
		multiplier = 1
		if angle < 0:
			multiplier = -1
		self.motor_stop = False
		def inField(field, thing):
			succes = 0
			j = 0
			for i in field:
				if j == 0:
					if i < thing:
						succes = 2
						break
				if j == len(field) - 1:
					if i > thing:
						succes = 3
						break 
				if thing == i:
					succes = 1
					break
				j = j + 1
			return succes
		
		field = range(angle-tolerance, angle+tolerance)
		
		while self.motor_stop == False:
			self.M1.run_forever(speed_sp=speed * direction)
			self.M2.run_forever(speed_sp=speed * direction)
			
			sleep(0.2)
			
			value = self.GS.value()
			
			if inField(field, value) == 2:
				#~ print("compesating 2")
				
				self.M1.run_forever(speed_sp=speed - 50 * direction)
				
				while self.GS.value() not in field:
					#~ sleep(0.02)
					print(self.GS.value())
				
				self.M1.run_forever(speed_sp=speed * direction)
				self.M2.run_forever(speed_sp=speed * direction)
				
			elif inField(field, value) == 3:
				print("compesating 3")
				
				self.M2.run_forever(speed_sp=speed - 50 * direction)
				
				while self.GS.value() not in field:
					#~ print(self.GS.value())
					sleep(0.02)
				
				self.M2.run_forever(speed_sp=speed * direction)
				self.M1.run_forever(speed_sp=speed * direction)
				
		if self.motor_stop is True:
			self.stopMotors()
	def measureDistanceStart(self):
		self.distance = self.M1.position
		
		# ~ self.MDistanceRunning = True
	
	
	def measureDistance(self, wheelDiameter = 5.5):
		turns = (self.M1.position - self.distance) / 360
		
		dist = turns * wheelDiameter * math.pi
		return dist + 14
	
	def measureDistanceRunning(self):
		return self.MDistanceRunning
	
	def stopMotors(self):
		self.motor_stop = True
		self.M2.stop()
		self.M1.stop()
		self.resetValue()
	def resetValue(self):
		self.GS.mode = 'GYRO-FAS'
		sleep(0.002)
		self.GS.mode = 'GYRO-ANG'
		sleep(0.001)
		
	def isRunning(self):
		return not self.motor_stop

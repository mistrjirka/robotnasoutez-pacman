#!/usr/bin/env python3

from ev3dev.ev3 import GyroSensor, LargeMotor
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
		self.stop = True
		self.wheelDiameter = wheelDiameter
		self.time = 0
		
	def turn(self, degrees, speed = 150, tolerance = 0.05):
		self.resetValue()
		self.stopMotors()
		self.tolerance = tolerance
		self.speed = speed
		multiplier = -1
		if degrees > 0:
			multiplier = 1
		self.GS.mode='GYRO-ANG'
		angle = self.GS.value()
		run = False
		breaker = False
		while True:
			if run == False:
				run = True
				self.M1.run_forever(speed_sp=self.speed * multiplier)
				self.M2.run_forever(speed_sp=self.speed * multiplier * -1)
				
			# ~ print ("debug of trueturn")
			# ~ print (math.ceil(degrees - self.tolerance * degrees))
			# ~ print (math.ceil(degrees + self.tolerance * degrees))
			print ("deg")
			print(self.GS.value())
			def check():
				field = range(math.ceil(degrees - self.tolerance * degrees), math.ceil(degrees + self.tolerance * degrees), multiplier)
				if angle - self.GS.value() in field:
					self.M2.stop()
					self.M1.stop()
					sleep(0.1)
					if angle - self.GS.value() not in field:
						if angle - self.GS.value() > field[len(field) - 1]:
							loc_multiplier = multiplier * -1
							while angle - self.GS.value() not in field:
								self.M1.run_forever(speed_sp=self.speed * loc_multiplier / 2)
								self.M2.run_forever(speed_sp=self.speed * loc_multiplier * -1 / 2)
								sleep(0.001)
							self.M2.stop()
							self.M1.stop()
							breaker = True
						elif angle - self.GS.value() < field[0]:
							loc_multiplier = multiplier * -1
							while angle - self.GS.value() not in field:
								self.M1.run_forever(speed_sp=self.speed * loc_multiplier / 2)
								self.M2.run_forever(speed_sp=self.speed * loc_multiplier * -1 / 2)
								sleep(0.001)
							self.M2.stop()
							self.M1.stop()
							breaker = True
					else:
						breaker = True
			check()
			if breaker:
				break
			sleep(0.002)
		self.resetValue()
		return True
	def straight(self, direction, speed, tolerance):
		self.resetValue()
		self.stopMotors()
		angle = self.GS.value()
		multiplier = 1
		if angle < 0:
			multiplier = -1
		self.stop = False
		def inField(field, thing):
			succes = 0
			j = 0
			for i in field:
				if j == 0:
					if i > thing:
						succes = 2
						break
				if j == len(field) - 1:
					if i < thing:
						succes = 3
						break 
				if thing == i:
					succes = 1
					break
				j = j + 1
			return succes
		field = range(angle-tolerance, angle+tolerance)
		while self.stop == False:
			self.M1.run_forever(speed_sp=speed * direction)
			self.M2.run_forever(speed_sp=speed * direction)
			sleep(0.2)
			value = self.GS.value()
			if inField(field, value) == 2:
				print("compesating")
				self.M1.run_forever(speed_sp=speed - 50 * direction)
				while self.GS.value() not in field:
					sleep(0.02)
				self.M1.run_forever(speed_sp=speed * direction)
				self.M2.run_forever(speed_sp=speed * direction)
			elif inField(field, value) == 3:
				print("compesating")
				self.M2.run_forever(speed_sp=speed - 50 * direction)
				while self.GS.value() not in field:
					sleep(0.02)
				self.M2.run_forever(speed_sp=speed * direction)
				self.M1.run_forever(speed_sp=speed * direction)
		if self.stop is True:
			self.stopMotors()
	def measureDistanceStart(self):
		self.time = timer()
	def measureDistanceStop(self):
		self.time = 0
	
	def distance(self, speed = 3.5):
		return (timer() - self.time) / 3.5 *(self.wheelDiameter * Math.pi)
	
	def stopMotors(self):
		self.stop = True
		self.M2.stop()
		self.M1.stop()
		self.resetValue()
	def resetValue(self):
		self.GS.mode = 'GYRO-RATE'
		self.GS.mode = 'GYRO-ANG'
	def isRunning(self):
		return not self.stop

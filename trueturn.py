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
		running = False
		self.breaker = False
		
		rightTurn = False # not actually right
		
		leftTurn = False # not actually left
		
		slowRightTurn = False # not actually right
		
		slowLeftTurn = False # not actually left
		
		field = range(math.ceil(degrees - self.tolerance * degrees), math.ceil(degrees + self.tolerance * degrees), multiplier)
		advancedField = range(math.ceil(degrees - 10 * degrees), math.ceil(degrees + 10 * degrees), multiplier)
		
		while angle - self.GS.value() not in field:
			
			if angle - self.GS.value() in advancedField:
				if abs(angle - self.GS.value()) <  abs(field[0]): #we have to make them absolute because we won to turn on both sides
					if not slowRightTurn:
						self.M1.run_forever(speed_sp=self.speed * multiplier / 2)
						self.M2.run_forever(speed_sp=self.speed * multiplier * -1 /2)
						slowRightTurn = True
						slowLeftTurn = False
						sleep(0.001)
				
				if abs(angle - self.GS.value()) > abs(field[len(field) - 1]): #we have to make them absolute because we won to turn on both sides
					if not leftTurn:
						self.M1.run_forever(speed_sp=self.speed * multiplier * -1 / 2)
						self.M2.run_forever(speed_sp=self.speed * multiplier / 2)
						slowRightTurn = False
						slowLeftTurn = True
						sleep(0.001)
			
			else:
				if abs(angle - self.GS.value()) <  abs(field[0]): #we have to make them absolute because we won to turn on both sides
					if not rightTurn:
						self.M1.run_forever(speed_sp=self.speed * multiplier)
						self.M2.run_forever(speed_sp=self.speed * multiplier * -1)
						rightTurn = True
						leftTurn = False
					else:
						sleep(0.002)
				
				if abs(angle - self.GS.value()) > abs(field[len(field) - 1]): #we have to make them absolute because we won to turn on both sides
					if not leftTurn:
						self.M1.run_forever(speed_sp=self.speed * multiplier * -1)
						self.M2.run_forever(speed_sp=self.speed * multiplier)
						rightTurn = False
						leftTurn = True
					else:
						sleep(0.002)
		sleep(0.1)
		
		leftTurn = False
		rightTurn = False
		slowLeftTurn = False
		slowRightTurn = False
		
		if angle - self.GS.value() not in field:
			while angle - self.GS.value() not in field:
				if abs(angle - self.GS.value()) <  abs(field[0]): #we have to make them absolute because we won to turn on both sides
					if not rightTurn:
						self.M1.run_forever(speed_sp=self.speed * multiplier / 2)
						self.M2.run_forever(speed_sp=self.speed * multiplier * -1 /2)
						rightTurn = True
						leftTurn = False
						sleep(0.001)
				
				if abs(angle - self.GS.value()) > abs(field[len(field) - 1]): #we have to make them absolute because we won to turn on both sides
					if not leftTurn:
						self.M1.run_forever(speed_sp=self.speed * multiplier * -1 / 2)
						self.M2.run_forever(speed_sp=self.speed * multiplier / 2)
						rightTurn = False
						leftTurn = True
						sleep(0.001)
		
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

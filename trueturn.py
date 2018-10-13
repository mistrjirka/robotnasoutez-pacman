#!/usr/bin/env python3

from ev3dev.ev3 import GyroSensor, LargeMotor
from time import sleep
import math
import asyncio

class TrueTurn:
	def __init__(self, motor1Port, motor2Port, gyroPort=None): #init
		if GyroSensor != None:
			self.GS = GyroSensor(gyroPort)
		else:
			self.GS = GyroSensor()
		self.M1 = LargeMotor(motor1Port)
		self.M2 = LargeMotor(motor2Port)
	def turn(self, degrees, speed = 150, tolerance = 0.05):
		self.tolerance = tolerance
		self.speed = speed
		multiplier = -1
		if degrees > 0:
			multiplier = 1
		self.GS.mode='GYRO-ANG'
		angle = self.GS.value()
		run = False
		while True:
			print ("Go")
			print(self.GS.value())
			print(str(angle - self.GS.value()) + " " + str(math.ceil(degrees - self.tolerance * degrees)) + " " + str(math.ceil(degrees + self.tolerance * degrees)))
			if run == False:
				run = True
				print("fuck")
				self.M1.run_forever(speed_sp=self.speed * multiplier)
				self.M2.run_forever(speed_sp=self.speed * multiplier * -1)
			if angle - self.GS.value() in range(math.ceil(degrees - self.tolerance * degrees),math.ceil(degrees + self.tolerance * degrees), multiplier):
				print("your")
				self.M2.stop()
				self.M1.stop()
				break
			sleep(0.002)
			print("self")
			print(self.GS.value())
			print(str(angle - self.GS.value()) + " " + str(math.ceil(degrees - self.tolerance * degrees)) + " " + str(math.ceil(degrees + self.tolerance * degrees)))
		return True
	def straight(self, direction, speed, tolerance):
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
			print (field)
			self.M1.run_forever(speed_sp=speed * direction)
			self.M2.run_forever(speed_sp=speed * direction)
			sleep(0.02)
			value = self.GS.value()
			if inField(field, value) == 2:
				self.M1.run_forever(speed_sp=speed - 50 * direction)
				while self.GS.value() not in field:
					print(self.GS.value())
					print("wrong")
					sleep(0.02)
				self.M1.run_forever(speed_sp=speed * direction)
				self.M2.run_forever(speed_sp=speed * direction)
			elif inField(field, value) == 3:
				self.M2.run_forever(speed_sp=speed - 50 * direction)
				while self.GS.value() not in field:
					print(self.GS.value())
					print("wrong")
					sleep(0.02)
				self.M2.run_forever(speed_sp=speed * direction)
				self.M1.run_forever(speed_sp=speed * direction)
			else:
				print("good")
	def Stop():
		self.stop = True
		self.M2.stop()
		self.M1.stop()
#!/usr/bin/env python3
from trueturn import TrueTurn
from time import sleep
from ev3dev.ev3 import UltrasonicSensor, MediumMotor, LargeMotor, TouchSensor, Screen
import asyncio

class Robot():
	def __init__(self, SM, mot1, mot2, GP = None, US = None, SM_speed = 900, SM_sleep = 0.2):
		
		if GP == None: #shitty
			self.TrueTurn = TrueTurn(mot1, mot2)
		else:
			self.TrueTurn = TrueTurn(mot1, mot2, GP)
		
		if US == None: #shitty
			self.US = UltrasonicSensor()
		else:
			self.US = UltrasonicSensor(US)
		
		self.mot1 = LargeMotor(mot1)
		self.mot2 = LargeMotor(mot2)
		self.SM = MediumMotor(SM)
		
		self.SM_speed = SM_speed
		self.SM_sleep = SM_sleep
		
	def sonicValue(self, tolerance = 5):
		cache = [1,20]
		while abs(cache[0] - cache[1]) > tolerance:
			cache[0] = self.US.value()/10 
			sleep(0.06)
			cache[1] = self.US.value()/10
			sleep(0.06)
		return sum(cache) / len(cache)
	
	def checkWay(self): #async function
		data = [0,0,0]
		
		self.SM.run_to_rel_pos(position_sp=0, speed_sp=self.SM_speed, stop_action="hold")
		sleep(self.SM_sleep)
		data[1] = self.sonicValue()
		
		self.SM.run_to_rel_pos(position_sp=90, speed_sp=self.SM_speed, stop_action="hold")
		sleep(self.SM_sleep)
		data[0] = self.sonicValue()
		
		self.SM.run_to_rel_pos(position_sp=-180, speed_sp=self.SM_speed, stop_action="hold")
		sleep(self.SM_sleep)
		data[2] = self.sonicValue()
		
		self.SM.run_to_rel_pos(position_sp=90, speed_sp=self.SM_speed, stop_action="hold")
		sleep(self.SM_sleep)
		return data
		# ~ callback(data)

	

if __name__ == "__main__":
	Main = Robot("outC", "outA", "outB")
	def runProgram():
		print(Main.checkWay())
		
	ts = TouchSensor()
	lcd = Screen()
	lcd.draw.rectangle((0,0,177,40), fill='black')
	lcd.draw.text((48,13),'Ready to Launch', fill='white')
	lcd.draw.text((36,80),'Launch ICBM')
	lcd.update()
	while True:
		sleep(0.05)
		if ts.value() == 1:
			runProgram()
	

	# ~ run = False #later
	# ~ loop = asyncio.get_event_loop() #python3.6
	# ~ loop.run_until_complete(asyncio.wait(Main.checkWay))
	# ~ loop.close()
	# ~ asyncio.run(Main.checkWay()) #python3.7
		

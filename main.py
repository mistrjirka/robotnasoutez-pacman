#!/usr/bin/env python3
from trueturn import TrueTurn
from time import sleep
from ev3dev.ev3 import UltrasonicSensor, MediumMotor, LargeMotor, TouchSensor, Screen
import asyncio

class Robot():
	def __init__(self, SM, mot1, mot2, GP = None, US = None, SM_speed = 900, SM_sleep = 0.2, critical_distance = 10, max_map_size = [10,10], turn_tolerance = 0.05, straight_tolerance = 2, motor_speed = 500, motor_speed_turning = 150):
		
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
		
		self.map = [[0 for x in range(max_map_size[0])] for y in range(max_map_size[1])]
		
		self.critical_distance = critical_distance
		
		self.turn_tolerance = turn_tolerance
		
		self.straight_tolerance = straight_tolerance
		
		self.motor_speed = motor_speed
		
		self.motor_speed_turning = motor_speed_turning
		
		self.stop_way_check = False
		
		self.async_return = {}
		
		def turnRight():
			self.TrueTurn.turn(90, self.motor_speed_turning, self.turn_tolerance)
		
		def turnLeft():
			self.TrueTurn.turn(-90, self.motor_speed_turning, self.turn_tolerance)
		
		def straight():
			self.TrueTurn.straight(1, self.motor_speed, self.straight_tolerance)
		
		def backward():
			self.TrueTurn.straight(-1, self.motor_speed, self.straight_tolerance)
		
		self.configArray = {
			"turnCounter": 0,
			
			"movement":[ #turn left
				{
					"index": 0,
					"type": -1,
					"deg": 90,
					"do": turnRight
				},
				{
					"index": 2,
					"type": 1,
					"deg": -90,
					"do": turnLeft
				},
				{
					"index": 1,
					"type": 0,
					"deg": 0,
					"do": straight
				},
				{
					"type": 0,
					"deg": 0,
					"do": backward
				}
			]
		}
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
	
	def cycle(self):
		
		print("start")
		loop = asyncio.new_event_loop()
		asyncio.set_event_loop(loop)
		result = loop.run_until_complete(self.asyncWayCheck("ways"))
		print("after waycheck")
		
		while True:
			print("loooooop")
			print(self.async_return["ways"])
			sleep(1)
		
	def arrayCheck(self, array, value, inverted = False):
		data = []
		if not inverted:
			for i in array:
				data.append(i > value)
		else:
			for i in array:
				data.append(not(i > value))
		return data
	
	def returnConfigArray(self):
		return self.config_array
	
	def setConfigArray(self, array):
		self.config_array = array
	
	async def asyncWayCheck(self, id_for_return):
		loop = asyncio.get_event_loop()
		
		async def checkWayAsync():
			while True:
				if self.stop_way_check:
					break
				self.async_return[id_for_return] = self.arrayCheck(self.checkWay(), self.critical_distance, False)
		
		coro = checkWayAsync()
		
		self.async_return = loop.run_until_complete(coro)

if __name__ == "__main__":
	Main = Robot("outC", "outA", "outB")
	def runProgram():
		Main.cycle()
		
	ts = TouchSensor()
	lcd = Screen()
	lcd.draw.rectangle((0,0,177,40), fill='black')
	lcd.draw.text((48,13),'Ready to Launch ICBM', fill='white')
	lcd.update()
	while True:
		sleep(0.05)
		if ts.value() == 1:
			runProgram()
			break
	

	# ~ run = False #later
	# ~ loop = asyncio.get_event_loop() #python3.6
	# ~ loop.run_until_complete(asyncio.wait(Main.checkWay))
	# ~ loop.close()
	# ~ asyncio.run(Main.checkWay()) #python3.7
		

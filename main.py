#!/usr/bin/env python3
from trueturn import TrueTurn
from time import sleep
from ev3dev.ev3 import UltrasonicSensor, MediumMotor, LargeMotor, TouchSensor, Screen
from threading import Thread 
import math

class Robot():
	def __init__(self, SM, mot1, mot2, GP = None, US = None, SM_speed = 1550, starting_point = [3,2], SM_sleep = 0.15, critical_distance = 20, max_map_size = [9,6], turn_tolerance = 0.01, straight_tolerance = 2, motor_speed = 100, motor_speed_turning = 100, block_size = 28):
		#this is intitial configuration
		if GP == None:
			self.TrueTurn = TrueTurn(mot1, mot2)
		else:
			self.TrueTurn = TrueTurn(mot1, mot2, GP)
		
		if US == None:
			self.US = UltrasonicSensor()
		else:
			self.US = UltrasonicSensor(US)
		
		self.mot1 = LargeMotor(mot1)
		self.mot2 = LargeMotor(mot2)
		
		self.SM = MediumMotor(SM)
		self.SM_speed = SM_speed
		self.SM_sleep = SM_sleep
		
		self.block_size = block_size
		
		self.map = self.createMap(max_map_size[0], max_map_size[1])
		
		self.critical_distance = critical_distance
		
		self.turn_tolerance = turn_tolerance
		
		self.straight_tolerance = straight_tolerance
		
		self.motor_speed = motor_speed
		
		self.motor_speed_turning = motor_speed_turning
		
		self.stop_way_check = False
		
		self.async_return = {}
		
		self.pause_way_check = False
		
		self.map_direction = 0 # 0 is up (default position); 1 is right; 2 is down; 3 is left
		
		self.stop_mapping = False
		
		self.pause_mapping = False
		
		self.measuring_position = starting_point
		
		self.map_direction_definitions = [
			{
				"x": 0,
				"y": 1
			},
			{
				"x": 1,
				"y": 0
			},
			{
				"x": 0,
				"y": -1 
			},
			{
				"x": -1,
				"y": 0
			}
		]
		
		self.map_config_array = [
			{
				"deg": 90,
				"axis": 1
			},
			{
				"deg": -90,
				"axis": -1
			},
			{
				"deg": 0,
				"axis": 0
			}
		]
		
		
		self.map_legend = {
			"robot": {
				"name": "robot",
				"free": True,
				"todo": False
			},
			"done": {
				"name": "done",
				"free": True,
				"todo": False
			},
			"todo": {
				"name": "todo",
				"free": True,
				"todo": True
			},
			"blocked": {
				"name": "blocked",
				"free": False,
				"todo": False
			}
		}
		
		def straight():
			print("running")
			if self.TrueTurn.isRunning() is not True:
				def do():
					self.TrueTurn.straight(1, self.motor_speed, self.straight_tolerance)
				
				t = Thread(target=do)
				t.start()
			sleep(0.5)
		
		def backward():
			if self.TrueTurn.isRunning() is not True:
				def do():
					self.TrueTurn.straight(-1, self.motor_speed, self.straight_tolerance)
				
				t = Thread(target=do)
				t.start()
			sleep(0.5)
		
		def afterTurn():
			straight()
			sleep(0.2)
			self.async_return["ways"] = self.checkWay()
			print(self.async_return["ways"])
			self.resumeSearch()
			sleep(0.1)
		
		def turnLeft():
			self.TrueTurn.stopMotors()
			self.pauseSearch()
			sleep(0.2)
			print("turning")
			self.TrueTurn.turn(-90, self.motor_speed_turning, self.turn_tolerance)
			sleep(0.2)
			# ~ self.mapTurn(self.map_config_array["right"])
			afterTurn()
			print ("end of turning")
		
		def turnRight():
			self.TrueTurn.stopMotors()
			self.pauseSearch()
			
			sleep(0.2)
			self.TrueTurn.turn(90, self.motor_speed_turning, self.turn_tolerance)
			sleep(0.2)
			print ("turning")
			# ~ self.mapTurn(self.map_config_array["right"])
			afterTurn()
			print ("end of turning")
		
		self.turn_counter = 0
		
		self.config_array = [ #turn left
			{
				"index": 1,
				"type": 0,
				"deg": 0,
				"do": straight
			},
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
				"index": -1,
				"type": 0,
				"deg": 0,
				"do": backward
			}
		]
		
	
	def sonicValue(self, tolerance = 10):
		cache = [1,100]
		while abs(cache[0] - cache[1]) > tolerance and not (cache[0] > self.critical_distance * 1.5 and cache[1] > self.critical_distance * 1.5):
			cache[0] = self.US.value()/10 
			sleep(0.025)
			cache[1] = self.US.value()/10
			sleep(0.025)
		return sum(cache) / len(cache)
	
	def checkWay(self): #async function
		data = [0,0,0]
		# ~ print("checkway")
		data[1] = self.sonicValue()
		sleep(self.SM_sleep)
		self.SM.run_to_rel_pos(position_sp=90, speed_sp=self.SM_speed, stop_action="hold")
		sleep(self.SM_sleep)
		data[0] = self.sonicValue()
		
		self.SM.run_to_rel_pos(position_sp=-180, speed_sp=self.SM_speed, stop_action="hold")
		sleep(self.SM_sleep*2)
		data[2] = self.sonicValue()
		
		self.SM.run_to_rel_pos(position_sp=90, speed_sp=self.SM_speed, stop_action="hold")
		sleep(self.SM_sleep/1.5)
		# ~ print("result")
		# ~ print(data)
		return data
	
	def cycle(self): #main function
		self.async_return["ways"] = self.checkWay()
		print("start")
		self.asyncWayCheck("ways")
		print("after waycheck")
		
		self.asyncMapping()
		
		while True:
			print("loop")
			print(self.async_return["ways"])
			print(self.arrayCheck(self.async_return["ways"], self.critical_distance))
			options = self.ArrayIndexCheck(self.arrayCheck(self.async_return["ways"], self.critical_distance), True)
			# ~ print("options")
			# ~ print(options)
			todo = self.decisionMaking(options)
			print(todo)
			todo["do"]()
			print("endofloop")
			
	
	def arrayCheck(self, array, value, inverted = False):
		data = []
		if not inverted:
			for i in array:
				data.append(i >= value)
		else:
			for i in array:
				data.append(not(i >= value))
		return data
	
	def returnConfigArray(self):
		return self.config_array
	
	def setConfigArray(self, array):
		self.config_array = array
	
	def asyncWayCheck(self, id_for_return):
		def checkWayAsync():
			self.stop_way_check = False
			while True:
				if self.stop_way_check:
					break
				if self.pause_way_check is not True:
					self.async_return[id_for_return] = self.checkWay()
				else:
					sleep(0.1)
		t = Thread(target=checkWayAsync)
		t.start()
	
	def ArrayIndexCheck(self, array, statement):
		index = 0
		data = []
		for x in array:
			print(statement)
			if x == statement:
				data.append(index)
			index += 1
		return data
	
	def decisionMaking(self, options):  #todo some very smart algorithm that will be using map
		for x in self.config_array:
			print (x)
			if x["index"] in options:
				return x
		
		for x in self.config_array:
			if x["index"] == -1:
				return x
	
	"""These three functions are for syncing searching with turning to prevent false results"""
	
	def pauseSearch(self):
		self.pause_way_check = True
	
	def resumeSearch(self):
		self.pause_way_check = False
	
	def destroySearch(self):
		self.stop_way_check = True
	
	def rawValue(self):
		return self.US.value()
	
	def createMap(self, x, y):
		cache = []
		for i in range (0,y):
			cache.append([])
			for j in range (0, x):
				cache[i].append("empty")
				
		return cache
		
	def mapTurn(self, event):
		self.to_do_mapping = event
	
	def asyncMapping(self):
		self.stop_mapping = False
		self.pause_mapping = False
		distance = 0
		
		self.TrueTurn.measureDistanceStart()
		
		def mapping():
			
			while not self.stop_mapping:
				if self.pause_mapping:
					sleep(0.07)
				else:
					ways = self.arrayCheck(self.async_return["ways"], self.critical_distance)
					
					direction = self.map_direction
					
					distance = self.TrueTurn.measureDistance()
					
					blocks = math.floor(distance / self.block_size)
					
					measuringPoint = self.measuring_position
					
					x = measuringPoint[0]
					
					if self.map_direction_definitions[direction]["x"] != 0:
						x += self.map_direction_definitions[direction]["x"] * blocks
					
					y = measuringPoint[1]
					
					if self.map_direction_definitions[direction]["y"] != 0:
						y += self.map_direction_definitions[direction]["y"] * blocks
					
					position = [x, y]
					
					print ("mapping")
					
					print(direction)
					
					print(distance)
					
					print (blocks)
					print (measuringPoint)
					print (position)
					
					self.map[position[0]][position[1]] = self.map[x][y] = self.map_legend["done"]
					
					if ways[0]: #left
						x = position[0] + self.map_direction_definitions[self.directionCorrection(direction + self.map_config_array[1]["axis"])]["x"]
						y = position[1] + self.map_direction_definitions[self.directionCorrection(direction + self.map_config_array[1]["axis"])]["y"]
						
						if self.map[x][y] == "empty":
							self.map[x][y] = self.map_legend["todo"]
					else:
						x = position[0] + self.map_direction_definitions[self.directionCorrection(direction + self.map_config_array[1]["axis"])]["x"]
						y = position[1] + self.map_direction_definitions[self.directionCorrection(direction + self.map_config_array[1]["axis"])]["y"]
						
						self.map[x][y] = self.map_legend["blocked"]
					
					if ways[2]: #right
						x = position[0] + self.map_direction_definitions[self.directionCorrection(direction + self.map_config_array[0]["axis"])]["x"]
						y = position[1] + self.map_direction_definitions[self.directionCorrection(direction + self.map_config_array[0]["axis"])]["y"]
						
						if self.map[x][y] == "empty":
							self.map[x][y] = self.map_legend["todo"]
					else:
						x = position[0] + self.map_direction_definitions[self.directionCorrection(direction + self.map_config_array[0]["axis"])]["x"]
						y = position[1] + self.map_direction_definitions[self.directionCorrection(direction + self.map_config_array[0]["axis"])]["y"]
						
						self.map[x][y] = self.map_legend["blocked"]
						
					if ways[1]: #straight
						x = position[0] + self.map_direction_definitions[self.directionCorrection(direction + self.map_config_array[2]["axis"])]["x"]
						y = position[1] + self.map_direction_definitions[self.directionCorrection(direction + self.map_config_array[2]["axis"])]["y"]
						
						if self.map[x][y] == "empty":
							self.map[x][y] = self.map_legend["todo"]
					else:
						x = position[0] + self.map_direction_definitions[self.directionCorrection(direction + self.map_config_array[2]["axis"])]["x"]
						y = position[1] + self.map_direction_definitions[self.directionCorrection(direction + self.map_config_array[2]["axis"])]["y"]
						
						self.map[x][y] = self.map_legend["blocked"]
					print("map")
					print(self.map)
					sleep(0.6)
				
				
		t = Thread(target=mapping)
		t.start()
	
	
	def directionCorrection(self, direction):
		finalDirection = direction
		
		def correcting(direction):
			correctedDirection = 0
			if direction > 3:
				correctedDirection = 0
				correctedDirection += direction - 4
			
			if direction < 0:
				correctedDirection = 4
				correctedDirection += direction
			return correctedDirection
		
		while finalDirection > 3 or finalDirection < 0:
			finalDirection = correcting(finalDirection)
			print(finalDirection) #debug
		
		return finalDirection
	
	def stopMapping(self):
		self.stop_mapping = True
	
	def pauseMapping(self):
		self.pause_mapping = True
	
	def resumeMapping(self):
		self.pause_mapping = False
	

if __name__ == "__main__":
	Main = Robot("outC", "outA", "outB", critical_distance = 20.5)
	def runProgram():
		Main.cycle()
		
	ts = TouchSensor()
	print ("ready to start")
	lcd = Screen()
	lcd.draw.text((48,13),'Ready to Launch ICBM', fill='white')
	lcd.update()
	while True:
		sleep(0.05)
		if ts.value() == 1:
			runProgram()
			break

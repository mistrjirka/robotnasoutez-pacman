#!/usr/bin/env python3
from trueturn import TrueTurn
from time import sleep
from ev3dev.ev3 import UltrasonicSensor, LargeMotor, TouchSensor, Screen
from ev3dev2.motor import MediumMotor
from threading import Thread 
import math
from json import dumps as stringify

class Robot():
	def __init__(self, SM, mot1, mot2, GP = None, US = None, SM_speed = 1560, starting_point = [4,2], SM_sleep = 0.1, critical_distance = 10, max_map_size = [9,6], turn_tolerance = 0.01, straight_tolerance = 1, motor_speed = 100, motor_speed_turning = 100, block_size = 28):
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
		
		self.SM.reset()
		self.position = starting_point
		
		self.block_size = block_size
		
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
		
		self.starting_point = starting_point
		
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
				"todo": False,
				"unkown": False
			},
			"todo": {
				"name": "todo",
				"free": True,
				"todo": True,
				"unkown": False
			},
			"blocked": {
				"name": "blocked",
				"free": False,
				"todo": False,
				"unkown": False
			},
			"empty":{
				"name": "empty",
				"free": False,
				"todo": True,
				"unkown": True
			}
		}
		
		self.map = self.createMap(max_map_size[0], max_map_size[1], self.map_legend["empty"])
		self.mes_map = self.createMap(max_map_size[0], max_map_size[1], {"blocked": 0, "free":0})
		
		self.decision_config = [
			self.calLeft,
			self.calStraight,
			self.calRight
		]
		
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
			self.pauseMapping()
			sleep(0.2)
			#~ print("turning")
			self.TrueTurn.turn(-90, self.motor_speed_turning, self.turn_tolerance)
			sleep(0.2)
			self.mapTurn(self.map_config_array[1])
			self.resumeMapping()
			afterTurn()
			#~ print ("end of turning")
		
		def turnRight():
			self.TrueTurn.stopMotors()
			self.pauseSearch()
			self.pauseMapping()
			sleep(0.2)
			self.TrueTurn.turn(90, self.motor_speed_turning, self.turn_tolerance)
			sleep(0.2)
			#~ print ("turning")
			self.mapTurn(self.map_config_array[0])
			self.resumeMapping()
			afterTurn()
			#~ print ("end of turning")
		
		self.turn_counter = 0
		
		self.config_array = [ #turn left
			{
				"index": 1,
				"type": 0,
				"deg": 0,
				"do": straight
			},
			{
				"index": 2,
				"type": -1,
				"deg": 90,
				"do": turnRight
			},
			{
				"index": 0,
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
		
		cache = []
		
		cache.append(self.US.value()/10)
		sleep(0.006)
		cache.append(self.US.value()/10)
		sleep(0.005)
		cache.append(self.US.value()/10)
		sleep(0.005)
		
		print(cache)
		
		biggest = max(cache)
		smallest = min(cache)
		
		biggestArray = []
		smallestArray = []
		
		for i in cache:
			if abs(biggest - i) <= abs(i - smallest):
				biggestArray.append(i)
			elif abs(biggest - i) >= abs(i - smallest):
				smallestArray.append(i)
		
		solution = []
		
		if len(biggestArray) > len(smallestArray):
			solution = biggestArray
		else: 
			solution = smallestArray
		
		return sum(solution) / len(solution)
	
	def checkWay(self): #async function
		data = [0,0,0]
		# ~ print("checkway")
		data[1] = self.sonicValue()
		self.SM.run_to_abs_pos(position_sp=90, speed_sp=self.SM_speed, stop_action="hold")
		sleep(self.SM_sleep)
		data[0] = self.sonicValue()
		
		self.SM.run_to_abs_pos(position_sp=-90, speed_sp=self.SM_speed, stop_action="hold")
		sleep(self.SM_sleep*2.2)
		data[2] = self.sonicValue()
		
		self.SM.run_to_abs_pos(position_sp=0, speed_sp=self.SM_speed, stop_action="hold")
		sleep(self.SM_sleep)
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
			#~ print("loop")
			#~ print(self.async_return["ways"])
			simplified = self.arrayCheck(self.async_return["ways"], self.critical_distance)
			# ~ options = self.ArrayIndexCheck(simplified, True)
			print (simplified)
			todo = self.decisionMaking(simplified)
			#~ print(todo)
			todo["do"]()
			#~ print("endofloop")
			
	
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
	
	def decisionMaking(self, notToUse):  #todo some very smart algorithm that will be using map
		
		def smartCheck(strict = True): # not really that smart 
			options = []
			i = 0
			
			def waycheck(strict = True):
				
				ways = [False, False, False]
				
				ind = 0
				
				for j in self.decision_config:
					cal = j(self.position, self.map_direction)
					x = cal[0]
					y = cal[1]
					if x < len(self.map) and y < len(self.map[0]) and x >= 0 and y >= 0:
						if strict:
							if self.map[x][y]["todo"]:
								ways[ind] = True
						else:
							if self.map[x][y]["free"]:
								ways[ind] = True
					ind += 1
				
				return ways
			
			ways = waycheck()
			
			if len(ways) == 0:
				waycheck(False)
			
			for z in ways:
				if z:
					cal = self.decision_config[i](self.position, self.map_direction)
					x = cal[0]
					y = cal[1]
					if x < len(self.map) and y < len(self.map[0]) and x >= 0 and y >= 0:
						print(cal)
						print(i)
						if strict:
							if self.map[x][y]["todo"]:
								options.append(i)
						else:
							options.append(i)
				
				i += 1 
			return options
		options = smartCheck()
		
		if len(options) == 0: #failsafe
			print("failsafe")
			options = smartCheck(False)
			
		
		print (options)
		for x in self.config_array:
			if x["index"] in options:
				return x
		
		for y in self.config_array:
			if y["index"] == -1:
				return y
	
	"""These three functions are for syncing searching with turning to prevent false results"""
	
	def pauseSearch(self):
		self.pause_way_check = True
	
	def resumeSearch(self):
		self.pause_way_check = False
	
	def destroySearch(self):
		self.stop_way_check = True
	
	def rawValue(self):
		return self.US.value()
	
	def createMap(self, x, y, fill):
		cache = []
		for i in range (0,x):
			cache.append([])
			for j in range (0, y):
				print (self)
				cache[i].append(fill.copy())
				
		return cache
		
	def mapTurn(self, event):
		self.map_direction = self.directionCorrection(self.map_direction + event["axis"])
		self.TrueTurn.measureDistanceStart()
		self.measuring_position = self.position
		
	def asyncMapping(self):
		self.stop_mapping = False
		self.pause_mapping = False
		distance = 0
		
		self.TrueTurn.measureDistanceStart()
		
		def mapping():
			
			while not self.stop_mapping:
				if self.pause_mapping:
					sleep(0.1)
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
					
					self.position = position
					
					#~ print ("mapping")
					
					#~ print(direction)
					
					#~ print(distance)
					
					#~ print (blocks)
					#~ print (measuringPoint)
					#~ print (position)
					
					def calcStatus(x,y):
						free = self.mes_map[x][y]["free"] / (self.mes_map[x][y]["free"] + self.mes_map[x][y]["blocked"])
						blocked = self.mes_map[x][y]["blocked"] / (self.mes_map[x][y]["free"] + self.mes_map[x][y]["blocked"])
						print("!!startofdebug!!")
						print("calculated")
						print(free)
						print(blocked)
						print([x,y])
						print("!!endofdebug!!")
						if free >= 0.7:
							return self.map_legend["todo"].copy()
							
						if blocked >= 0.7:
							return self.map_legend["blocked"].copy()
						print("Here")
						
						if blocked < 0.7 and free < 0.7:
							return self.map_legend["blocked"].copy()
					
					self.map[position[0]][position[1]] = self.map_legend["done"]
					
					if ways[0]: #left
						cal = self.calLeft(position, direction)
						#~ print("left")
						#~ print(cal)
						#~ print("from")
						#~ print(position)
						x = cal[0]
						y = cal[1]
						if x < len(self.map) and y < len(self.map[0]) and x >= 0 and y >= 0:
							if self.map[x][y]["name"] != "done":
								self.mes_map[x][y]["free"] += 1
								
								self.map[x][y] = calcStatus(x,y)
					else:
						print("ways left")
						print(ways)
						cal = self.calLeft(position, direction)
						x = cal[0]
						y = cal[1]
						#~ print("left")
						#~ print(cal)
						#~ print("from")
						#~ print(position)
						if x < len(self.map) and y < len(self.map[0]) and x >= 0 and y >= 0:
							if self.map[x][y]["name"] != "done":
								print("left")
								self.mes_map[x][y]["blocked"] += 1
								
								self.map[x][y] = calcStatus(x,y)
					
					if ways[2]: #right
						cal = self.calRight(position, direction)
						x = cal[0]
						y = cal[1]
						#~ print("right")
						#~ print(cal)
						#~ print("from")
						#~ print(position)
						if x < len(self.map) and y < len(self.map[0]) and x >= 0 and y >= 0:
							if self.map[x][y]["name"] != "done":
								self.mes_map[x][y]["free"] += 1
								
								self.map[x][y] = calcStatus(x,y)
					else:
						print("ways right")
						print(ways)
						cal = self.calRight(position, direction)
						x = cal[0]
						y = cal[1]
						#~ print("right")
						#~ print(cal)
						#~ print("from")
						#~ print(position)
						if x < len(self.map) and y < len(self.map[0]) and x >= 0 and y >= 0:
							if self.map[x][y]["name"] != "done":
								print("right")
								self.mes_map[x][y]["blocked"] += 1
								
								self.map[x][y] = calcStatus(x,y)
						
					if ways[1]: #straight
						cal = self.calStraight(position, direction)
						x = cal[0]
						y = cal[1]
						#~ print("straight")
						#~ print(cal)
						#~ print("from")
						#~ print(position)
						if x < len(self.map) and y < len(self.map[0]) and x >= 0 and y >= 0:
							if self.map[x][y]["name"] != "done" :
								self.mes_map[x][y]["free"] += 1
								
								self.map[x][y] = calcStatus(x,y)
					else:
						print("ways straight")
						print(ways)
						cal = self.calStraight(position, direction)
						x = cal[0]
						y = cal[1]
						#~ print("straight")
						#~ print(cal)
						#~ print("from")
						#~ print(position)
						if x < len(self.map) and y < len(self.map[0]) and x >= 0 and y >= 0:
							if self.map[x][y]["name"] != "done":
								print("straight")
								self.mes_map[x][y]["blocked"] += 1
								
								self.map[x][y] = calcStatus(x,y)
					#~ print("map")
					#~ print(self.map)
					
					print(self.mes_map)
					
					fh = open("/var/www/html/map.txt","w")
					fh.write(stringify(self.map))
					fh.close()
					
					fh2 = open("/var/www/html/mesmap.txt","w")
					fh2.write(stringify(self.mes_map))
					fh2.close()
					
					sleep(0.1)
				
				
		t = Thread(target=mapping)
		t.start()
	
	
	def calLeft(self, position, direction):
		return [
			position[0] + self.map_direction_definitions[self.directionCorrection(direction + self.map_config_array[1]["axis"])]["x"], 
			position[1] + self.map_direction_definitions[self.directionCorrection(direction + self.map_config_array[1]["axis"])]["y"]
		]
	
	def calRight(self, position, direction):
		return [
			position[0] + self.map_direction_definitions[self.directionCorrection(direction + self.map_config_array[0]["axis"])]["x"],
			position[1] + self.map_direction_definitions[self.directionCorrection(direction + self.map_config_array[0]["axis"])]["y"]
		]
	
	def calStraight(self, position, direction):
		return [
			position[0] + self.map_direction_definitions[self.directionCorrection(direction + self.map_config_array[2]["axis"])]["x"],
			position[1] + self.map_direction_definitions[self.directionCorrection(direction + self.map_config_array[2]["axis"])]["y"]
		]
	
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
	Main = Robot("outC", "outA", "outB", critical_distance = 22.5)
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

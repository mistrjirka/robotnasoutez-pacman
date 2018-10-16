#!/usr/bin/env python3
from trueturn import TrueTurn
from time import sleep
from ev3dev.ev3 import UltrasonicSensor, MediumMotor, LargeMotor, Button
import asyncio

class Robot():
	def __init__(self, SM, mot1, mot2, GP = None, US = None, SM_speed = 900, SM_sleep = 0.5):
		
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
		print(cache)
		while abs(cache[0] - cache[1]) > tolerance:
			cache[0] = self.US.value()/10 
			print(cache[0])
			sleep(0.06)
			cache[1] = self.US.value()/10
			sleep(0.06)
		print(sum(cache) / len(cache))
		return sum(cache) / len(cache)
	
	def checkWay(self): #async function
		data = [0,0,0]
		
		self.SM.run_to_rel_pos(position_sp=0, speed_sp=self.SM_speed, stop_action="hold")
		sleep(self.SM_sleep)
		data[0] = self.sonicValue()
		
		self.SM.run_to_rel_pos(position_sp=90, speed_sp=self.SM_speed, stop_action="hold")
		sleep(self.SM_sleep)
		data[1] = self.sonicValue()
		
		self.SM.run_to_rel_pos(position_sp=-180, speed_sp=self.SM_speed, stop_action="hold")
		sleep(self.SM_sleep)
		data[2] = self.sonicValue()
		
		self.SM.run_to_rel_pos(position_sp=90, speed_sp=self.SM_speed, stop_action="hold")
		sleep(self.SM_sleep)
		
		# ~ callback(data)

	

if __name__ == "__main__":
	Main = Robot("outC", "outA", "outB")
	def runProgram():
		Main.checkWay()
	Btn = Button()
	
	Btn.on_right = runProgram
	print("click on right button or autodestrucion is needed")
	sleep(1)
	print("autodestrucion in 5s")
	sleep(5)
	print("BOOOM")

	# ~ run = False #later
	# ~ loop = asyncio.get_event_loop() #python3.6
	# ~ loop.run_until_complete(asyncio.wait(Main.checkWay))
	# ~ loop.close()
	# ~ asyncio.run(Main.checkWay()) #python3.7
		

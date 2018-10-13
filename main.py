#!/usr/bin/env python3
import trueturn
from time import sleep
from ev3dev.ev3 import UltrasonicSensor, MediumMotor, LargeMotor

class Robot():
	def __init__(self, SM, mot1, mot2, GP = None, US = None):
		
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
		
		self.SM_speed = 900
		self.SM_sleep = 0.5
	def checkWay(self, US):
		data = [0,0,0]
		
		self.SM.run_to_rel_pos(position_sp=0, speed_sp=self.SM_speed, stop_action="hold")
		sleep(self.SM_sleep)
		
		self.SM.run_to_rel_pos(position_sp=90, speed_sp=self.SM_speed, stop_action="hold")
		sleep(self.SM_sleep)
		
		self.SM.run_to_rel_pos(position_sp=-180, speed_sp=self.SM_speed, stop_action="hold")
		sleep(self.SM_sleep)
		
		self.SM.run_to_rel_pos(position_sp=0, speed_sp=self.SM_speed, stop_action="hold")
		sleep(self.SM_sleep)
		

if __name__ == "__main__":
	Main = Robot("OutC", "OutA", "OutB")

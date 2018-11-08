from time import sleep
from ev3dev.ev3 import MediumMotor, UltrasonicSensor
us = UltrasonicSensor()
SM = MediumMotor("outC")

def sonicValue(tolerance = 10):
	cache = [1,100]
	while abs(cache[0] - cache[1]) > tolerance and not (cache[0] > 21.5 and cache[1] > 21.5):
		cache[0] = us.value()/10 
		sleep(0.025)
		cache[1] = us.value()/10
		sleep(0.025)
	return sum(cache) / len(cache)

data = [0,0,0]
while True:
	data[1] = sonicValue()
	SM.run_to_rel_pos(position_sp=90, speed_sp=1550, stop_action="hold")
	sleep(0.16)
	data[0] = sonicValue()
	SM.run_to_rel_pos(position_sp=-180, speed_sp=1550, stop_action="hold")
	sleep(0.35)
	data[2] = sonicValue()
	SM.run_to_rel_pos(position_sp=90, speed_sp=1550, stop_action="hold")
	sleep(0.2)
	


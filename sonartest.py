from ev3dev2.motor import MediumMotor
from ev3dev2.sensor.lego import UltrasonicSensor

US = UltrasonicSensor()
MM = MediumMotor()

def sonicValue(tolerance = 10):
	cache = [1,100]
	while abs(cache[0] - cache[1]) > tolerance and not (cache[0] > 30 * 1.5 and cache[1] > 30* 1.5):
		cache[0] = US.value()/10 
		sleep(0.025)
		cache[1] = US.value()/10
		sleep(0.025)
	return sum(cache) / len(cache)

def checkWay(): #async function
	sleep_time = 0.05
	data = [0,0,0]
	# ~ print("checkway")
	data[1] = sonicValue()
	sleep(sleep_time)
	MM.run_to_rel_pos(position_sp=90, speed_sp=1550, stop_action="hold")
	sleep(sleep_time)
	data[0] = sonicValue()
	
	MM.run_to_rel_pos(position_sp=-180, speed_sp=1550, stop_action="hold")
	sleep(sleep_time*2)
	data[2] = sonicValue()
	
	MM.run_to_rel_pos(position_sp=90, speed_sp=1550, stop_action="hold")
	sleep(sleep_time/1.5)
	# ~ print("result")
	# ~ print(data)
	return data

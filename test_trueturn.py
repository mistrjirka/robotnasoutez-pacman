from trueturn import TrueTurn
from time import sleep
test = TrueTurn("outA", "outB")
test.turn(90)
test.straight(1,400,2)
sleep(10)
test.stop()

from trueturn import TrueTurn
from time import sleep
test = TrueTurn("outA", "outB")
test.turn(90)
test.straight(1,2,400)
sleep(10)
test.stop()

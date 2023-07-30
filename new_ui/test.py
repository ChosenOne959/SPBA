import airsim
import cv2
import numpy as np
import os
import time
import tempfile

# connect to the AirSim simulator
client = airsim.MultirotorClient()
client.confirmConnection()
client.enableApiControl(True)
client.armDisarm(True)
client.takeoffAsync().join()
print("API Control enabled: %s" % client.isApiControlEnabled())
print("Multirotor_Rotor_Speed:",client.getRotorStates())
client.landAsync().join()
print("Multirotor_Rotor_Speed:",client.getRotorStates().rotors[1])

#restore to original state
client.reset()

client.enableApiControl(False)
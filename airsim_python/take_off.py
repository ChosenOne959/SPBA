import airsim
# connect to the AirSim simulator
client = airsim.MultirotorClient()
client.confirmConnection()
# get control
client.enableApiControl(True)
# unlock
client.armDisarm(True)
# Async methods returns Future. Call join() to wait for task to complete.
client.takeoffAsync().join()
client.moveToZAsync(-40,5).join()
client.landAsync().join()
# lock
client.armDisarm(False)

# release control
client.enableApiControl(False)
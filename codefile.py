import airsim
remote_host = '202.120.37.157'
Drone1 = airsim.MultirotorClient(ip=remote_host)
Drone1.confirmConnection()
Drone1.enableApiControl(True)
Drone1.armDisarm(True)
Drone1.takeoffAsync().join()
Drone1.moveByVelocityAsync(0,1,0,3).join()
Drone1.landAsync().join()
Drone1.armDisarm(False)
Drone1.enableApiControl(False)
from asyncore import write
import airsim
# connect to the AirSim simulator
client = airsim.MultirotorClient()
client.confirmConnection()
client.simEnableWeather(True)
client.simSetWeatherParameter(airsim.WeatherParameter.Rain,2)
client.simSetWeatherParameter(airsim.WeatherParameter.Fog,0.6)
client.simSetWeatherParameter(airsim.WeatherParameter.Dust,0.6)
client.simGetCollisionInfo()
#client.simSetWeatherParameter(airsim.WeatherParameter.Snow,2)
# get control
client.enableApiControl(True)
# unlock
client.armDisarm(True)
# Async methods returns Future. Call join() to wait for task to complete.
client.takeoffAsync().join()
client.moveToZAsync(-20,2).join()
response = client.simGetImage(camera_name='0', image_type=0)
f = open('photo1.png','wb')
f.write(response)
f.close()
client.moveByVelocityAsync(-5,0,0,50).join()
client.moveToZAsync(-5,2).join()
client.landAsync().join()
# lock
client.armDisarm(False)

# release control
client.enableApiControl(False)

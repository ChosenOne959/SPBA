import airsim

def weather_adjust(rain,snow,fog):
    remote_host = '202.120.37.157'
    client = airsim.MultirotorClient(ip=remote_host)
    client.simEnableWeather(True)
    client.simSetWeatherParameter(airsim.WeatherParameter.Rain, rain)
    client.simSetWeatherParameter(airsim.WeatherParameter.Snow, snow)
    client.simSetWeatherParameter(airsim.WeatherParameter.Fog, fog)

import airsim
import keyboard
velocity=3;
duration=0.02
ratio=3
velocity_shift=velocity*ratio
AirSim_client = airsim.MultirotorClient()
AirSim_client.enableApiControl(True)
AirSim_client.armDisarm(True)
"""
take off and land
"""
keyboard.add_hotkey('t', lambda: AirSim_client.takeoffAsync())
keyboard.add_hotkey('l', lambda: AirSim_client.landAsync())
"""
up--forward
down--back
LEFT--turn left
RIGHT--turn right
a--raise height
d--lower height
"""
keyboard.add_hotkey('LEFT', lambda: AirSim_client.moveByVelocityBodyFrameAsync(0,-velocity,0,duration=duration))
keyboard.add_hotkey('RIGHT', lambda: AirSim_client.moveByVelocityBodyFrameAsync(0,velocity,0,duration=duration))
keyboard.add_hotkey('up', lambda: AirSim_client.moveByVelocityBodyFrameAsync(velocity,0,0,duration=duration))
keyboard.add_hotkey('down', lambda: AirSim_client.moveByVelocityBodyFrameAsync(-velocity,0,0,duration=duration))
keyboard.add_hotkey('a', lambda: AirSim_client.moveByVelocityBodyFrameAsync(0,0,-velocity,duration=duration))
keyboard.add_hotkey('d', lambda: AirSim_client.moveByVelocityBodyFrameAsync(0,0,velocity,duration=duration))

keyboard.add_hotkey('up+LEFT', lambda: AirSim_client.moveByVelocityBodyFrameAsync(velocity,-velocity,0,duration=duration))
keyboard.add_hotkey('up+RIGHT', lambda: AirSim_client.moveByVelocityBodyFrameAsync(velocity,velocity,0,duration=duration))
keyboard.add_hotkey('up+a', lambda: AirSim_client.moveByVelocityBodyFrameAsync(velocity,0,-velocity,duration=duration))
keyboard.add_hotkey('up+d', lambda: AirSim_client.moveByVelocityBodyFrameAsync(velocity,0,velocity,duration=duration))

keyboard.add_hotkey('down+LEFT', lambda: AirSim_client.moveByVelocityBodyFrameAsync(-velocity,-velocity,0,duration=duration))
keyboard.add_hotkey('down+RIGHT', lambda: AirSim_client.moveByVelocityBodyFrameAsync(-velocity,velocity,0,duration=duration))
keyboard.add_hotkey('down+a', lambda: AirSim_client.moveByVelocityBodyFrameAsync(-velocity,0,-velocity,duration=duration))
keyboard.add_hotkey('down+d', lambda: AirSim_client.moveByVelocityBodyFrameAsync(-velocity,0,velocity,duration=duration))


keyboard.add_hotkey('a+RIGHT', lambda: AirSim_client.moveByVelocityBodyFrameAsync(0,velocity,-velocity,duration=duration))
keyboard.add_hotkey('a+LEFT', lambda: AirSim_client.moveByVelocityBodyFrameAsync(0,-velocity,-velocity,duration=duration))

keyboard.add_hotkey('d+RIGHT', lambda: AirSim_client.moveByVelocityBodyFrameAsync(0,velocity,velocity,duration=duration))
keyboard.add_hotkey('d+LEFT', lambda: AirSim_client.moveByVelocityBodyFrameAsync(0,-velocity,velocity,duration=duration))

"""
    left shift--increase the veloctiy
"""
keyboard.add_hotkey('LEFT+left shift', lambda: AirSim_client.moveByVelocityBodyFrameAsync(0,-velocity_shift,0,duration=duration))
keyboard.add_hotkey('RIGHT+left shift', lambda: AirSim_client.moveByVelocityBodyFrameAsync(0,velocity_shift,0,duration=duration))
keyboard.add_hotkey('up+left shift', lambda: AirSim_client.moveByVelocityBodyFrameAsync(velocity_shift,0,0,duration=duration))
keyboard.add_hotkey('down+left shift', lambda: AirSim_client.moveByVelocityBodyFrameAsync(-velocity_shift,0,0,duration=duration))
keyboard.add_hotkey('a+left shift', lambda: AirSim_client.moveByVelocityBodyFrameAsync(0,0,-velocity_shift,duration=duration))
keyboard.add_hotkey('d+left shift', lambda: AirSim_client.moveByVelocityBodyFrameAsync(0,0,velocity_shift,duration=duration))

keyboard.add_hotkey('left shift+up+LEFT', lambda: AirSim_client.moveByVelocityBodyFrameAsync(velocity_shift,-velocity_shift,0,duration=duration))
keyboard.add_hotkey('left shift+up+RIGHT', lambda: AirSim_client.moveByVelocityBodyFrameAsync(velocity_shift,velocity_shift,0,duration=duration))
keyboard.add_hotkey('left shift+up+a', lambda: AirSim_client.moveByVelocityBodyFrameAsync(velocity_shift,0,-velocity_shift,duration=duration))
keyboard.add_hotkey('left shift+up+d', lambda: AirSim_client.moveByVelocityBodyFrameAsync(velocity_shift,0,velocity_shift,duration=duration))

keyboard.add_hotkey('left shift+down+LEFT', lambda: AirSim_client.moveByVelocityBodyFrameAsync(-velocity_shift,-velocity_shift,0,duration=duration))
keyboard.add_hotkey('left shift+down+RIGHT', lambda: AirSim_client.moveByVelocityBodyFrameAsync(-velocity_shift,velocity_shift,0,duration=duration))
keyboard.add_hotkey('left shift+down+a', lambda: AirSim_client.moveByVelocityBodyFrameAsync(-velocity_shift,0,-velocity_shift,duration=duration))
keyboard.add_hotkey('left shift+down+d', lambda: AirSim_client.moveByVelocityBodyFrameAsync(-velocity_shift,0,velocity_shift,duration=duration))


keyboard.add_hotkey('left shift+a+RIGHT', lambda: AirSim_client.moveByVelocityBodyFrameAsync(0,velocity_shift,-velocity_shift,duration=duration))
keyboard.add_hotkey('left shift+a+LEFT', lambda: AirSim_client.moveByVelocityBodyFrameAsync(0,-velocity_shift,-velocity_shift,duration=duration))

keyboard.add_hotkey('left shift+d+RIGHT', lambda: AirSim_client.moveByVelocityBodyFrameAsync(0,velocity_shift,velocity_shift,duration=duration))
keyboard.add_hotkey('left shift+d+LEFT', lambda: AirSim_client.moveByVelocityBodyFrameAsync(0,-velocity_shift,velocity_shift,duration=duration))

keyboard.wait('q')
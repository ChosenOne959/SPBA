is_localhost=True

def set_value(value):
    global is_localhost
    is_localhost = value

def get_value():
    return is_localhost
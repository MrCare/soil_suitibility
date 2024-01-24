'''
Author: Mr.Car
Date: 2024-01-07 23:07:27
'''
def PD(value):
    return value

def TCHD(value):
    value = int(value)
    result = None
    if value >= 100:
        result = 0
    elif value >= 85 and value < 100:
        result = 1
    elif value >= 75 and value < 85:
        result = 2
    elif value >= 60 and value < 75:
        result = 3
    elif value >= 30 and value < 60:
        result = 4
    else:
        result = 5
    return result

def DBLSFD(value):
    return value

def TRZD(value):
    return value

def SZYTJ(value):
    return value

def PSNL(value):
    return value

def TRZJSWR(value):
    return value
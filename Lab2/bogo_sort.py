import random
import time

def bogoSort(data, drawData, timer):
    while not is_sorted(data):
        shuffle(data)
        drawData(data, ['Red' for _ in range(len(data))])
        time.sleep(timer)

def is_sorted(data):
    for i in range(len(data) - 1):
        if data[i] > data[i + 1]:
            return False
    return True

def shuffle(data):
    random.shuffle(data)

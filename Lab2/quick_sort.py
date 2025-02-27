import time

def quicksort(data, low, high, drawData, speed):
    if low < high:
        pi = partition(data, low, high, drawData, speed)
        quicksort(data, low, pi - 1, drawData, speed)
        quicksort(data, pi + 1, high, drawData, speed)
        drawData(data, ['Blue' for _ in range(len(data))])

def partition(data, low, high, drawData, speed):
    pivot = data[high]
    i = low - 1

    for j in range(low, high):
        if data[j] < pivot:
            i += 1
            data[i], data[j] = data[j], data[i]
            drawData(data, ['Green' if x == i or x == j else 'Red' for x in range(len(data))])
            time.sleep(speed)

    data[i + 1], data[high] = data[high], data[i + 1]
    drawData(data, ['Green' if x == i + 1 or x == high else 'Red' for x in range(len(data))])
    time.sleep(speed)
    
    return i + 1

import time

# Heapify function with visualization updates
def heapify(arr, n, i, drawData, speed):
    largest = i  
    l = 2 * i + 1  
    r = 2 * i + 2  

    if l < n and arr[l] > arr[largest]:
        largest = l

    if r < n and arr[r] > arr[largest]:
        largest = r

    if largest != i:
        arr[i], arr[largest] = arr[largest], arr[i]

        drawData(arr, ['Green' if x == i or x == largest else 'Red' for x in range(len(arr))])
        time.sleep(speed)

        heapify(arr, n, largest, drawData, speed)

# Heap Sort function with visualization
def heapSort(arr, drawData, speed):
    n = len(arr)

    for i in range(n // 2 - 1, -1, -1):
        heapify(arr, n, i, drawData, speed)

    for i in range(n - 1, 0, -1):
        arr[0], arr[i] = arr[i], arr[0]  

        drawData(arr, ['Green' if x == i else 'Red' for x in range(len(arr))])
        time.sleep(speed)

        heapify(arr, i, 0, drawData, speed)

    drawData(arr, ['Blue' for _ in range(len(arr))])  # Final sorted state

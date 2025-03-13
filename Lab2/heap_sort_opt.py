import time

def heap_sort_optimized(arr, drawData, speed):

    n = len(arr)

    for i in range(n // 2 - 1, -1, -1):
        heapify(arr, n, i, drawData, speed)

    for i in range(n - 1, 0, -1):
        arr[i], arr[0] = arr[0], arr[i] 
        drawData(arr, ['Green' if x == i else 'Red' for x in range(len(arr))])
        time.sleep(speed)

        heapify(arr, i, 0, drawData, speed)

    drawData(arr, ['Blue' for _ in range(len(arr))])

def heapify(arr, n, i, drawData, speed):

    while True:
        largest = i
        left = 2 * i + 1
        right = 2 * i + 2

        if left < n and arr[left] > arr[largest]:
            largest = left
        if right < n and arr[right] > arr[largest]:
            largest = right

        if largest == i:
            break

        arr[i], arr[largest] = arr[largest], arr[i]
        drawData(arr, ['Green' if x == i or x == largest else 'Red' for x in range(len(arr))])
        time.sleep(speed)

        i = largest 

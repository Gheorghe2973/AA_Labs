import time

def merge_sort_optimized(data, drawData, speed, threshold=10):
    n = len(data)

    if n <= threshold:
        insertion_sort(data, drawData, speed)
        return

    size = 1
    while size < n:
        for left in range(0, n, 2 * size):
            mid = min(left + size - 1, n - 1)
            right = min(left + 2 * size - 1, n - 1)

            merge_in_place(data, left, mid, right, drawData, speed)

        size *= 2 
def merge_in_place(data, left, mid, right, drawData, speed):
    i, j = left, mid + 1

    while i <= mid and j <= right:
        if data[i] <= data[j]:
            i += 1
        else:
            value = data[j]
            index = j
            while index > i:
                data[index] = data[index - 1]
                index -= 1
            data[i] = value

            i += 1
            mid += 1
            j += 1

        drawData(data, ['Green' if left <= x <= right else 'Red' for x in range(len(data))])
        time.sleep(speed)

def insertion_sort(data, drawData, speed):

    for i in range(1, len(data)):
        key = data[i]
        j = i - 1
        while j >= 0 and data[j] > key:
            data[j + 1] = data[j]
            j -= 1
        data[j + 1] = key

        drawData(data, ['Blue' for _ in range(len(data))])
        time.sleep(speed)

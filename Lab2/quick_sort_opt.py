import time

def quicksort_optimized(data, drawData, speed):
    stack = [(0, len(data) - 1)]  

    while stack:
        low, high = stack.pop()
        if low < high:
            pivot_index = hoare_partition(data, low, high, drawData, speed)

            drawData(data, ['Green' if low <= x <= high else 'Red' for x in range(len(data))])
            time.sleep(speed)

            if pivot_index - low > high - pivot_index:
                stack.append((low, pivot_index))
                stack.append((pivot_index + 1, high))
            else:
                stack.append((pivot_index + 1, high))
                stack.append((low, pivot_index))

def hoare_partition(data, low, high, drawData, speed):
    pivot = data[low] 
    i, j = low - 1, high + 1

    while True:
        while True:
            i += 1
            if data[i] >= pivot:
                break
        while True:
            j -= 1
            if data[j] <= pivot:
                break

        if i >= j:
            return j  

        data[i], data[j] = data[j], data[i]
        drawData(data, ['Green' if x == i or x == j else 'Red' for x in range(len(data))])
        time.sleep(speed)

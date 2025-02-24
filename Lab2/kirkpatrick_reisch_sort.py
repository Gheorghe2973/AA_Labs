import time

def kirkpatrick_reisch_sort(arr, drawData, speed):
    n = len(arr)
    if n <= 1:
        return arr

    step = 1
    while step < n:
        merged = []
        for i in range(0, n, 2 * step):
            left = arr[i:i + step]
            right = arr[i + step:i + 2 * step]
            merged += merge(left, right, drawData, speed)
        arr[:] = merged
        drawData(arr, ['Green' if x < step else 'Red' for x in range(len(arr))])
        time.sleep(speed)
        step *= 2
    
    drawData(arr, ['Blue' for _ in range(len(arr))])  # Final sorted state

def merge(left, right, drawData, speed):
    merged = []
    i = j = 0

    while i < len(left) and j < len(right):
        if left[i] < right[j]:
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1
        drawData(merged + left[i:] + right[j:], ['Yellow' for _ in range(len(merged + left[i:] + right[j:]))])
        time.sleep(speed)

    merged.extend(left[i:])
    merged.extend(right[j:])
    return merged

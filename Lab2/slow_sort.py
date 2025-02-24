import time

def slow_sort(arr, left, right, drawData, speed):
    if left >= right:
        return

    mid = (left + right) // 2
    slow_sort(arr, left, mid, drawData, speed)
    slow_sort(arr, mid + 1, right, drawData, speed)

    if arr[right] < arr[mid]:
        arr[right], arr[mid] = arr[mid], arr[right]

        drawData(arr, ['Green' if left <= x <= right else 'Red' for x in range(len(arr))])
        time.sleep(speed)

    slow_sort(arr, left, right - 1, drawData, speed)

    drawData(arr, ['Blue' for _ in range(len(arr))])  # Final sorted state

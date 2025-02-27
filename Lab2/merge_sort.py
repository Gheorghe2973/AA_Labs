import time

def merge(arr, left, mid, right, drawData, speed):
    n1 = mid - left + 1
    n2 = right - mid

    L = arr[left:mid + 1]
    R = arr[mid + 1:right + 1]

    i, j, k = 0, 0, left

    while i < n1 and j < n2:
        if L[i] <= R[j]:
            arr[k] = L[i]
            i += 1
        else:
            arr[k] = R[j]
            j += 1
        k += 1
        drawData(arr, ['Green' if left <= x <= right else 'Red' for x in range(len(arr))])
        time.sleep(speed)

    while i < n1:
        arr[k] = L[i]
        i += 1
        k += 1
        drawData(arr, ['Green' if left <= x <= right else 'Red' for x in range(len(arr))])
        time.sleep(speed)

    while j < n2:
        arr[k] = R[j]
        j += 1
        k += 1
        drawData(arr, ['Green' if left <= x <= right else 'Red' for x in range(len(arr))])
        time.sleep(speed)

def merge_sort(arr, left, right, drawData, speed):
    if left < right:
        mid = (left + right) // 2

        merge_sort(arr, left, mid, drawData, speed)
        merge_sort(arr, mid + 1, right, drawData, speed)
        merge(arr, left, mid, right, drawData, speed)
        drawData(arr, ['Blue' for _ in range(len(arr))]) 

import time

def bucket_sort(arr, drawData, speed):
    if len(arr) == 0:
        return arr

    bucket_count = len(arr)
    min_value, max_value = min(arr), max(arr)

    # Create empty buckets
    buckets = [[] for _ in range(bucket_count)]

    for num in arr:
        index = int((num - min_value) / (max_value - min_value + 1) * (bucket_count - 1))
        buckets[index].append(num)

    drawData(arr, ['Yellow' for _ in range(len(arr))])
    time.sleep(speed)

    sorted_arr = []
    for bucket in buckets:
        bucket.sort()
        sorted_arr.extend(bucket)
        drawData(sorted_arr + [min(arr)] * (len(arr) - len(sorted_arr)), ['Green' for _ in range(len(arr))])
        time.sleep(speed)

    arr[:] = sorted_arr
    drawData(arr, ['Blue' for _ in range(len(arr))])  # Final sorted state

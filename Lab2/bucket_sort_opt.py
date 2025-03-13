import time

def bucket_sort_optimized(arr, drawData, speed):
    if len(arr) == 0:
        return

    min_value, max_value = min(arr), max(arr)
    bucket_count = max(1, int(len(arr) ** 0.5)) 

    buckets = [[] for _ in range(bucket_count)]

    range_size = (max_value - min_value) / bucket_count if max_value > min_value else 1
    for num in arr:
        index = int((num - min_value) / range_size)
        index = min(index, bucket_count - 1)
        buckets[index].append(num)

    drawData(arr, ['Yellow' for _ in range(len(arr))])
    time.sleep(speed)

    sorted_index = 0
    for bucket in buckets:
        insertion_sort(bucket) 
        for num in bucket:
            arr[sorted_index] = num
            sorted_index += 1
            drawData(arr, ['Green' if x <= sorted_index else 'Red' for x in range(len(arr))])
            time.sleep(speed)

    drawData(arr, ['Blue' for _ in range(len(arr))]) 

def insertion_sort(bucket):
    """Efficient Insertion Sort for small bucket arrays."""
    for i in range(1, len(bucket)):
        key = bucket[i]
        j = i - 1
        while j >= 0 and bucket[j] > key:
            bucket[j + 1] = bucket[j]
            j -= 1
        bucket[j + 1] = key

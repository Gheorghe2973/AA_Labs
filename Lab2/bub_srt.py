import time

def bubble(data, drawData, timer):
	n = len(data)
	
	for i in range(n):
		for j in range(0, n-i-1):
			
			if data[j] > data[j+1]:
				data[j], data[j+1] = data[j+1], data[j]
				
				# if swapped then color becomes Green else stays Red
				drawData(data, ['Green' if x == j +
								1 else 'Red' for x in range(len(data))])
				time.sleep(timer)
		
	# sorted elements generated with Green color
	drawData(data, ['Green' for x in range(len(data))])

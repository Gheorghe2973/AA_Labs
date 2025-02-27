from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import random
import time
from bub_srt import bubble
from quick_sort import quicksort
from merge_sort import merge_sort
from heap_sort import heapSort
from kirkpatrick_reisch_sort import kirkpatrick_reisch_sort
from slow_sort import slow_sort
from bucket_sort import bucket_sort
from bogo_sort import bogoSort

# Initialize root class for Tkinter
root = Tk()
root.attributes('-fullscreen', True)
root.title("Sorting Algorithm Visualizer")
root.config(bg="Grey")

select_alg = StringVar()
data = []
sorting = False  # Variable to track sorting state

# Function to generate data values
def generate():
    global data, sorting
    sorting = False  # Reset sorting state
    minval = int(minEntry.get())
    maxval = int(maxEntry.get())
    sizeval = int(sizeEntry.get())
    
    data = [random.randrange(minval, maxval + 1) for _ in range(sizeval)]
    drawData(data, ['Red' for _ in range(len(data))])

# Function to create data bars
def drawData(data, colorlist):
    canvas.delete("all")
    can_height = 800  # Increased height for more space
    can_width = 1870
    x_width = can_width / (len(data) + 1)
    offset = 30
    spacing = 10
    
    normalized_data = [i / max(data) for i in data]
    
    for i, height in enumerate(normalized_data):
        x0 = i * x_width + offset + spacing
        y0 = can_height - height * 600  # Increased bar height
        x1 = (i + 1) * x_width + offset
        y1 = can_height
        
        canvas.create_rectangle(x0, y0, x1, y1, fill=colorlist[i])
        canvas.create_text(x0 + 2, y0, anchor=SE, text=str(data[i]))
    
    root.update_idletasks()

# Function to start sorting
def start_algorithm():
    global data, sorting
    sorting = True
    start_time = time.time()  # Record start time
    
    if select_alg.get() == "Bubble Sort":
        bubble(data, drawData, speedbar.get())
    elif select_alg.get() == "Quick Sort":
        quicksort(data, 0, len(data) - 1, drawData, speedbar.get())
    elif select_alg.get() == "Merge Sort":
        merge_sort(data, 0, len(data) - 1, drawData, speedbar.get())
    elif select_alg.get() == "Heap Sort":
        heapSort(data, drawData, speedbar.get())
    elif select_alg.get() == "Kirkpatrick-Reisch Sort":
        kirkpatrick_reisch_sort(data, drawData, speedbar.get())
    elif select_alg.get() == "Slow Sort":
        slow_sort(data, 0, len(data) - 1, drawData, speedbar.get())
    elif select_alg.get() == "Bucket Sort":
        bucket_sort(data, drawData, speedbar.get())
    elif select_alg.get() == "Bogo Sort":
        bogoSort(data, drawData, speedbar.get())

    end_time = time.time()  # Record end time
    sorting_time = round(end_time - start_time, 5)  # Calculate and round to 5 decimal places

    messagebox.showinfo("Sorting Completed", f"Sorting took {sorting_time} seconds!")


# Function to exit application
def exit_app():
    root.destroy()

# UI Frame
Mainframe = Frame(root, width=1400, height=100, bg="Grey")
Mainframe.pack(side=TOP, fill=X)

canvas = Canvas(root, width=1400, height=700, bg="Grey")
canvas.pack(side=TOP, pady=10, expand=True, fill=BOTH)  

# Algorithm selection menu
Label(Mainframe, text="ALGORITHM", bg='Grey').grid(row=0, column=0, padx=5, pady=5, sticky=W)
algmenu = ttk.Combobox(Mainframe, textvariable=select_alg, values=["Bubble Sort", "Quick Sort", "Merge Sort", "Heap Sort", "Kirkpatrick-Reisch Sort", "Slow Sort", "Bucket Sort", "Bogo Sort"])
algmenu.grid(row=0, column=1, padx=5, pady=5)
algmenu.current(0)

# Start button
Button(Mainframe, text="START", bg="Blue", command=start_algorithm).grid(row=1, column=3, padx=5, pady=5)


# Exit button
Button(Mainframe, text="EXIT", bg="Red", command=exit_app).grid(row=1, column=5, padx=5, pady=5)

# Speed control
speedbar = Scale(Mainframe, from_=0.10, to=2.0, length=100, digits=2, resolution=0.2, orient=HORIZONTAL, label="Select Speed")
speedbar.grid(row=0, column=2, padx=5, pady=5)

# Data size selection
sizeEntry = Scale(Mainframe, from_=3, to=60, resolution=1, orient=HORIZONTAL, label="Size")
sizeEntry.grid(row=1, column=0, padx=5, pady=5)

# Min value selection
minEntry = Scale(Mainframe, from_=0, to=10, resolution=1, orient=HORIZONTAL, label="Minimum Value")
minEntry.grid(row=1, column=1, padx=5, pady=5)

# Max value selection
maxEntry = Scale(Mainframe, from_=10, to=100, resolution=1, orient=HORIZONTAL, label="Maximum Value")
maxEntry.grid(row=1, column=2, padx=5, pady=5)

# Generate button
Button(Mainframe, text="Generate", bg="Red", command=generate).grid(row=0, column=3, padx=5, pady=5)

# Tkinter main loop
root.mainloop()

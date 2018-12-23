import psutil
import time

NUMofCPU = 0
CPUtotal = 0.0
CPUtotalFreq = []
CPUperCore = []

VirtualMem = 0

DiskPartitions = 0
RootDiskUse = 0

def GetCPU():
    NUMofCPU = psutil.cpu_count(logical=False) #Return only physical cores (NOT logical)
    CPUtotal = psutil.cpu_percent()
    CPUtotalFreq = psutil.cpu_freq(percpu=True)
    CPUperCore = psutil.cpu_percent(percpu=True)

    print("Number for physical CPU cores: ", NUMofCPU)
    print("CPU Total useage: ", CPUtotal)
    print("CPU Total Frequency: ", CPUtotalFreq)
    print("Per Core CPU useage: ", CPUperCore)

def GetRAM():
    VirtualMem = psutil.virtual_memory()

    print("RAM: ", VirtualMem)

def GetDisks():
    DiskPartitions = psutil.disk_partitions()
    RootDiskUse = psutil.disk_usage('/') #Provide disk path

    print("Disk Partitions", DiskPartitions)
    print("Root Disk Use", RootDiskUse)

#Every ten seconds, grab system info and print to console
while(1):
    GetCPU()
    GetRAM()
    GetDisks()
    time.sleep(10)

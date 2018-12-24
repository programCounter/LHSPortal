import psutil
import time

#CPU Var
NUMofCPU = 0
NUMofTHREAD = 0
CPUtotal = 0.0
CPUtotalFreq = []
CPUperCore = []

#RAM Var
VirtualMem = 0

#Disk Var
DiskPartitions = 0
RootDiskUse = 0

def GetCPU():
    NUMofCPU = psutil.cpu_count(logical=False) #Return only physical cores (NOT logical)
    NUMofTHREAD = psutil.cpu_count(logical=True) #Return number of logical threads
    CPUtotal = psutil.cpu_percent()
    CPUtotalFreq = psutil.cpu_freq(percpu=True)
    CPUperCore = psutil.cpu_percent(percpu=True)

    #print("Number for physical CPU cores: ", NUMofCPU)
    #print("Number of CPU threads: ", NUMofTHREAD)
    #print("CPU Total useage: ", CPUtotal)
    #print("CPU Total Frequency: ", CPUtotalFreq)
    #print("Per Core CPU useage: ", CPUperCore)

def GetRAM():
    VirtualMem = psutil.virtual_memory()

    #print("RAM: ", VirtualMem)

def GetDisks():
    DiskPartitions = psutil.disk_partitions()
    RootDiskUse = psutil.disk_usage('/') #Provide disk path

    #print("Disk Partitions", DiskPartitions)
    #print("Root Disk Use", RootDiskUse)


def ReadSYS():
    '''
    This function can be called externally to run all other functions
    in the script.
    '''

    GetCPU()
    GetRAM()
    GetDisks()

    return('NUMofCPU':NUMofCPU, 'NUMofTHREAD':NUMofTHREAD, 'CPUtotal':CPUtotal, 'CPUtotalFreq':CPUtotalFreq, 'CPUperCore':CPUperCore, 'VirtualMem':VirtualMem, 'DiskPartitions':DiskPartitions, 'RootDiskUse':RootDiskUse)

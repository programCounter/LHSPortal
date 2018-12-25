#libraries To include
import psutil


def GetCPU():
    NUMofCPU = psutil.cpu_count(logical=False) #Return only physical cores (NOT logical)
    NUMofTHREAD = psutil.cpu_count(logical=True) #Return number of logical threads
    CPUtotal = psutil.cpu_percent()
    CPUtotalFreq = psutil.cpu_freq(percpu=True)
    CPUperCore = psutil.cpu_percent(percpu=True)


def GetRAM():
    VirtualMem = psutil.virtual_memory()


def GetDisks():
    DiskPartitions = psutil.disk_partitions()
    RootDiskUse = psutil.disk_usage('/') #Provide disk path


def ReadSYS():
    '''
    This function can be called externally to gather system data.
    '''

    NUMofCPU = psutil.cpu_count(logical=False) #Return only physical cores (NOT logical)
    NUMofTHREAD = psutil.cpu_count(logical=True) #Return number of logical threads
    CPUtotal = psutil.cpu_percent()
    CPUperCore = psutil.cpu_percent(percpu=True)

    VirtualMem = psutil.virtual_memory()

    DiskPartitions = psutil.disk_partitions()
    RootDiskUse = psutil.disk_usage('/') #Provide disk path


    return{ 'NUMofCPU':NUMofCPU, 'NUMofTHREAD':NUMofTHREAD, 'CPUtotal':CPUtotal, 'CPUperCore':CPUperCore, 'VirtualMem':VirtualMem, 'DiskPartitions':DiskPartitions, 'RootDiskUse':RootDiskUse }

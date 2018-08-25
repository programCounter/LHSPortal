import os

#DiskName = os.statvfs("MOUNTPOINT")
def CheckSpace():
    boot = os.statvfs("/home/pi/riley")
    NAS = os.statvfs("/home/pi/NAS")
    PMS = os.statvfs("/home/pi/PMS")
    Archive = os.statvfs("/home/pi/Archive")
    bootLocal = os.statvfs("/home/pi")

    disks = [boot, NAS, PMS, Archive, bootLocal]
    disksName = ["LHS Boot", "NAS", "PMS", "Archive", "LHSWeb Boot"]

    y = 0

    totalBytes = []
    totalUsedSpace = []
    totalSpaceAvaliable = []
    usedPercent = []

    for x in disks:
        totalBytes.append((float(x.f_bsize * x.f_blocks))/1024/1024/1024)
        totalUsedSpace.append((float(x.f_bsize * (x.f_blocks - x.f_bfree)))/1024/1024/1024)
        totalSpaceAvaliable.append((float(x.f_bsize * x.f_bfree))/1024/1024/1024)

        usedPercent.append(((float(x.f_bsize * (x.f_blocks - x.f_bfree)))/1024/1024/1024)/((float(x.f_bsize * x.f_blocks))/1024/1024/1024))

        #print("Disk: %s" % disksName[y])
        #print("Total Disk Space: %.2fGB" % (totalBytes/1024/1024/1024))
        #print("Total Used Space: %.2fGB" % (totalUsedSpace/1024/1024/1024))
        #print("Total Space Avliable: %.2fGB" % (totalSpaceAvaliable/1024/1024/1024))
        #print("--------------------------------------------------------")

        y = y + 1

    return totalBytes, totalUsedSpace, totalSpaceAvaliable, disksName, usedPercent

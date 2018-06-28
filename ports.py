#Modified port checker tool from the original PCheckLogger.py app
#Riley Larche June 2018

#Python V3.6.5
#Atom V1.27.2

'''
This application is for use inside of the LHS web app. It cuts out functions from the front end.
If something is needed for single use applications please do not use this script.
'''


#Imports
import socket, datetime, time
from os.path import exists

def check(IPaddress, port):
    """Function that checks the port and returns it. The main web app will deal with moving to and from database."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    stat = sock.connect_ex((IPaddress, port))

    if stat == 0:
        Active = True
    else:
        Active = False

    return Active

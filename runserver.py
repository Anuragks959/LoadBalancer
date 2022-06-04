import os

num=5
for i in range(1,num+1):
    cmd = "python server.py server-"+str(i)+" "+str(5000+i)
    os.system('start /MIN cmd /k '+cmd)
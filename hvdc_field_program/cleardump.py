import os

os.chdir("dump")
for f in os.listdir(os.getcwd()):
    try:
        os.remove(f)
    except PermissionError:
        pass
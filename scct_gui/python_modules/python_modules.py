
import os
from ctypes import cdll, c_char_p

def main():
    path = os.path.dirname(os.path.realpath(__file__))

    # Load the shared library
    try:
        go_modules = cdll.LoadLibrary(path+'/../go_modules/go_modules.so')
    except Exception as e:
        print(str(e)+'\n Try running `python ./gupy.py gopherize -t <target_platform> -n <app_name>`')
        return

    # Define the return type of the function
    go_modules.go_module.restype = c_char_p

    # Call the Go function and decode the returned bytes to a string
    result = go_modules.go_module().decode('utf-8')

    return result

if __name__ == "__main__":
    main() 


    
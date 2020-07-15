import sys
import os


# main
def main():

    os.chdir("./py/")
    files = os.listdir("./")
    files.sort(key=lambda x: x.lower())
    listing = []
    index = 1

    for f in files:
        s = f.split(".")
        if len(s) > 1 and s[1] == "py":
                print("Running", f)
                os.system("python {0}".format(f))



if __name__ == "__main__":
    main()
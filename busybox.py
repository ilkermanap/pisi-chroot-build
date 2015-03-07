import os, sys, subprocess


BUSYBOX="/bin/busybox"

class Busybox:
    def __init__(self, dizin):
        self.dizin = dizin
        os.system("mkdir -p %s/bin" % self.dizin)
        print 2
        self.komut_kur()

    def komut_kur(self):
        print 11
        liste = os.popen("%s --list" % BUSYBOX).readlines()
        print 12
        os.chdir(self.dizin)
        for komut in liste:
            os.symlink(BUSYBOX, "bin/%s" % komut.strip())


if (__name__=="__main__"):
    x = Busybox(sys.argv[1])

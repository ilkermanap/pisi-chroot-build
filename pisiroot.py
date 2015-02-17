
import os, sys, uuid, syslog, subprocess, glob

"""
https://github.com/evolve-os/repository/blob/master/system/base/pisi/files/evobuild.sh

Used the script above.
"""

class RootFS:
    def __init__(self):
        self.repo = "http://farm.pisilinux.org/.nofarm-repo/x86_64/pisi-index.xml.xz"
        self.cache = "/var/cache/pisi/packages"
        os.system("mkdir -p %s" % self.cache)
        self.rootdir = "/var/pisi/rootfs-%s" % uuid.uuid1()
        self.rootdir = "/var/pisi/rootfs-test"

        self.pisicmd = "pisi it --ignore-comar --ignore-safety -D %s/ -y" % self.rootdir
        print self.rootdir
        os.system("mkdir -p %s" % self.rootdir)
        self.pisipackages = glob.glob("%s/*" % self.cache)
        self.mounts = ["/proc", "/sys", "/var/cache/pisi/packages"]
        self.links = []
        self.mountDirs()
        self.symlinks()
        self.installBase()
        self.copyFiles()
        self.mknods()
        self.runCommand("pisi ar pisirepo %s" % self.repo)



    def mknods(self):
        self.runCommand("mknod /dev/console c 5 1")
        self.runCommand("mknod /dev/null c 1 3")
        self.runCommand("mknod /dev/random c 1 8")
        self.runCommand("mknod /dev/urandom c 1 9")

    def copyFiles(self):
        cmd = "cp /etc/resolv.conf %s/etc/." % self.rootdir
        os.system(cmd)

    def installBase(self):
        for pkg in self.pisipackages:
            cmd = "%s --ignore-dep  %s" % (self.pisicmd, pkg)
            print cmd
            os.system(cmd)

    def runCommand(self, cmd):
        os.system("chroot %s  %s" % (self.rootdir, cmd) )

    def symlinks(self):
        for link in self.links:
            os.system("mkdir -p %s%s" % (self.rootdir, link[:link.rfind("/")]))
            cmd = "ln -s %s %s%s" % (link, self.rootdir, link[:link.rfind("/")])
            os.system(cmd)


    def mountDirs(self, umount = False):
        if umount == False:
            for m in self.mounts:
                os.system("mkdir -p %s%s" % (self.rootdir, m))
                os.system("mount --bind %s %s%s" % (m, self.rootdir, m))
        else:
            for m in self.mounts:
                os.system("umount  %s%s" % (self.rootdir, m))

    def download(self):
        pass

    def clean(self):
        self.mountDirs(umount = True)

    def addpkg(self, pkgdir):
        cmd = "cp -r %s/* %s/root/pkg/." % (pkgdir, self.rootdir)
        os.system("mkdir -p %s/root/pkg" % self.rootdir)
        os.system(cmd)

if __name__ == "__main__":
    x = RootFS()
    x.addpkg(sys.argv[1])
    x.runCommand("pisi bi  /root/pkg/pspec.xml")
    x.clean()

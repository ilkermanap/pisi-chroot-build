import os, sys, uuid, syslog, subprocess, glob
import time
"""
https://github.com/evolve-os/repository/blob/master/system/base/pisi/files/evobuild.sh

Used the script above.
"""

global CACHEDIR
CACHEDIR= "/var/cache/pisi/packages"

BASE = "zlib-32bit gc mpfr libunwind elfutils gmp libgomp openldap-client gnutls utempter python-psutil"

class PisiPackage:
    """
    Basic pisi package operations class
    During init, it will search the local cache,
    if name isn't found, then it will fetch the
    package from remote repository.
    """
    def __init__(self, pname):
        self.filename = self.findInCache(pname)
        self.name = pname
        if self.filename == False:
            self.retrieve(pname)
            self.filename = self.findInCache(pname)


    def checkFile(self, fname, pname):
        n = fname.split("/")[-1]
        cmd = "pisi info %s > /tmp/%s.info" % (fname, n)
        os.system(cmd)
        f = open("/tmp/%s.info" % n ).readlines()
        for line in f:
            if line.find("Name") > -1:
                fpkgname = line.split(":")[1].split(",")[0].strip()
                if pname == fpkgname:
                    return True
        return False

    def findInCache(self, name):
        """
        Check if the package file is in cache
        return filename if found,
        else return False
        Package file        : ncurses-devel-5.9-5-p01-x86_64.pisi
        Name                : ncurses-devel, version: 5.9, release: 5

        """
        # FIXME
        # asagidaki glob satiri, paket ismine karsilik he zaman dogru
        # calismayabiiyor.. ornek, zlib-32bit ile zlib
        # zlib isteyip, zlib-32bit alabiliriz..
        # dosya adi ile pisi info almaya calistigimda, bazi paketlerde
        # os.popen, subprocess.check_output, ya da os.system komutlarinin
        # hepsi de komutu bitiremiyor..  ornek pisilinux-dev-tools
        #
        files = glob.glob("%s/%s-[0-9]*" % (CACHEDIR, name))
        if len(files) > 0:
            print files[-1], name
            #inf = os.popen("pisi info %s" % files[-1]).readlines()
            #print inf[1]
            latest = files[-1]
            return latest
        return False

    def retrieve(self, name):
        """
        Retrieve the package from repository
        """
        currpath = os.getcwd()
        os.chdir(CACHEDIR)
        os.system("pisi fc %s" % name)
        os.chdir(currpath)

    def install(self, basedir, ignoredep = False):
        """
        Install the package

        In default it will ignore dependencies.
        if you don't want to ignore dependencies,
        use it as below:

            pkg.install("/tmp/rootfs", ignoredep = False)

        With ignoredep = True:
            pkg.install("/tmp/rootfs")

        """
        cmd = "pisi it --ignore-comar"
        if ignoredep == True:
            cmd += " --ignore-dep"
        cmd += " -D %s -y %s  " % (basedir, self.filename)
        print cmd
        os.system(cmd)

class Packages:
    """
    This class allows us to define package groups.
    Just pass the name of packages in a string separated
    with whitespace.

    games = Packages("boswars tetris")
    games.packages["boswars"].install("/tmp/rootfs")

    or to install all

    for pkgname, pkg in games.packages.items():
       pkg.install("/tmp/rootfs")

    """
    def __init__(self, liststr = ""):
        pkgs = liststr.split()
        self.packages = {}
        for pkg in pkgs:
            self.packages[pkg] = PisiPackage(pkg)

    def addPackage(self, name):
        self.packages[name] = PisiPackage(name)

class RootFS:
    def __init__(self, pkgdir):
        self.pkgdir = pkgdir.split("/")[-1]
        self.base = Packages(liststr = BASE)
        self.buildDeps = Packages()
        self.repo = "http://farm.pisilinux.org/.nofarm-repo/x86_64/pisi-index.xml.xz"
        self.cache = "/var/cache/pisi/packages"
        os.system("mkdir -p %s" % self.cache)
        self.rootdir = "/var/pisi/rootfs-%s" % self.pkgdir

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
        self.runCommand("groupadd -g 18 messagebus")
        self.runCommand('useradd -m -d /var/run/dbus -r -s /bin/false -u 18 -g 18 messagebus -c "D-Bus Message Daemon"')
        self.copyFile("/usr/libexec/dbus-daemon-launch-helper", "/usr/lib/dbus-1.0")
        self.runCommand("dbus-uuidgen --ensure")
        self.runCommand("dbus-daemon --system")
        self.runCommand("chmod o+x /usr/lib/dbus-1.0/dbus-daemon-launch-helper")
        self.runCommand("pisi configure-pending")

    def mknods(self):
        self.runCommand("mknod /dev/console c 5 1")
        self.runCommand("mknod /dev/null c 1 3")
        self.runCommand("mknod /dev/random c 1 8")
        self.runCommand("mknod /dev/urandom c 1 9")
        cmd = "pisi up -dvys"
        self.runCommand(cmd)

    def copyFile(self, filename, newpath = ""):
        if newpath ==  "":
            path = filename[:filename.rfind("/")]
            oldname = filename
        else:
            path = newpath
            oldname = filename
            filename = "%s/%s" % (newpath,filename.split("/")[-1])

        pathcmd = "mkdir -p %s/%s" % (self.rootdir, path)
        print "pathcmd = ", pathcmd
        os.system(pathcmd)
        cmd = "cp %s %s/%s" % (oldname, self.rootdir, filename)
        print "copy cmd = ", cmd
        os.system(cmd)

    def copyFiles(self):
        os.system("cp /usr/share/baselayout/* %s/etc/." % self.rootdir)
        self.copyFile("/etc/resolv.conf")

    def installBase(self):
        cmd = "pisi ar farm -D %s %s" % (self.rootdir, self.repo)
        os.system(cmd)
        for pkgname, pkg in self.base.packages.items():
            pkg.install(self.rootdir, True)

        cmd = "pisi it -c system.base -y --ignore-comar -D %s" % self.rootdir
        os.system(cmd)
        cmd = "pisi it -c system.devel -y --ignore-comar -D %s" % self.rootdir
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

    def clean(self):
        self.mountDirs(umount = True)

    def findDeps(self, tag, ignoreDep = False):

        from xml.dom import minidom

        pspec = minidom.parse("%s/root/pkg/pspec.xml" % self.rootdir)
        alldeps = pspec.getElementsByTagName(tag)
        if len(alldeps) > 0:
            deps = alldeps[0].getElementsByTagName("Dependency")
            for d in deps:
                print d.toxml()
                deppkg = d.toxml().split(">")[1].split("<")[0]
                self.buildDeps.addPackage(deppkg)

            for pkgname, pkg in self.buildDeps.packages.items():
                pkg.install(self.rootdir, ignoreDep)


    def addpkg(self, pkgdir):
        cmd = "cp -r %s/* %s/root/pkg/." % (pkgdir, self.rootdir)
        os.system("mkdir -p %s/root/pkg" % self.rootdir)
        os.system(cmd)

if __name__ == "__main__":
    x = RootFS(sys.argv[1])
    x.addpkg(sys.argv[1])
    x.findDeps("BuildDependencies")
    x.findDeps("RuntimeDependencies")

    x.runCommand("pisi  --ignore-action-errors --ignore-safety bi   /root/pkg/pspec.xml")
    x.clean()

import os, sys, uuid, syslog, subprocess, glob

"""
https://github.com/evolve-os/repository/blob/master/system/base/pisi/files/evobuild.sh

Used the script above.
"""

global CACHEDIR
CACHEDIR= "/var/cache/pisi/packages"

BASE = "acl attr baselayout bash binutils catbox coreutils file gawk gcc glibc glibc-devel gmp grep kernel-headers libcap  libffi libgcc libmpc libpcre make mpfr ncurses openssl pisi python readline sed zlib autoconf automake diffutils   gnuconfig libtool piksemel ca-certificates  comar-api curl gperftools  leveldb  libgcrypt libgpg-error libidn      libssh2 libunwind pisilinux-dev-tools pisilinux-python  plyvel pycurl python python3 python-pyliblzma run-parts    snappy urlgrabber xz"


class PisiPackage:
    """
    Basic pisi package operations class
    During init, it will search the local cache,
    if name isn't found, then it will fetch the
    package from remote repository.
    """
    def __init__(self, pname):
        self.filename = self.findInCache(pname)
        if self.filename == False:
            self.retrieve(pname)
            self.filename = self.findInCache(pname)

    def findInCache(self, name):
        """
        Check if the package file is in cache
        return filename if found, 
        else return False
        """
        files = glob.glob("%s/%s*" % (CACHEDIR, name))
        if len(files) > 0:
            latest = files[-1]
            return latest
        else:
            return False

    def retrieve(self, name):
        """
        Retrieve the package from repository
        """
        currpath = os.getcwd()
        os.chdir(CACHEDIR)
        os.system("pisi fc %s" % name)
        os.chdir(currpath)

    def install(self, basedir, ignoredep = True):
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


class RootFS:
    def __init__(self):
        self.base = Packages(BASE)
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
        for pkgname, pkg in self.base.packages.items():
            pkg.install(self.rootdir)

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

    def addpkg(self, pkgdir):
        cmd = "cp -r %s/* %s/root/pkg/." % (pkgdir, self.rootdir)
        os.system("mkdir -p %s/root/pkg" % self.rootdir)
        os.system(cmd)

if __name__ == "__main__":
    x = RootFS()
    x.addpkg(sys.argv[1])
    x.runCommand("pisi bi  /root/pkg/pspec.xml")
    x.clean()

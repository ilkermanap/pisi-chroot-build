import os, sys
from kayit import Kayit

ROOTFS=sys.argv[1]
liste = open("paketler.txt").readlines()

class Paket:
    def __init__(self, dosya_adi,  target):
        self.adi = dosya_adi
        self.unzip(target)
        self.clean()

    def unzip(self, target):
        print self.adi
        os.system("unzip %s 2>/dev/null" % self.adi)
        os.system("cd %s; tar Jxf ../install.tar.xz" % target)

    def clean(self):
        os.system("rm -rf comar; rm -f install.tar.xz; rm -f *.xml")

class Busybox(Paket):
    def unzip(self, target):
        Paket.unzip(self, target)
        symlinks = open("%s/bin/busybox.links" % target, "r").readlines()
        for link in symlinks:
            try:
                path = link[:link.rfind("/")]
                src = "/bin/busybox"
                os.system("mkdir -p %s/%s" % (target, path))
                os.symlink(src, "%s/%s" % (target, link[:-1]))
            except:
                pass

class Chroot:
    def __init__(self, dizin, paketListesi):
        self.pisilog = Kayit("%s-pisi.log" % dizin)
        self.rootlog = Kayit("%s-root.log" % dizin)
        self.buildlog = Kayit("%s-build.log" % dizin)
        self.runOutside("rm -rf %s" % dizin)
        self.runOutside("mkdir -p %s" % dizin)
        self.root = dizin
        self.mounts = ["/proc", "/sys"]
        self.mountDirs()
        self.installPackages(paketListesi)
        self.runOutside("cp %s/usr/share/baselayout/* %s/etc/." % (self.root, self.root))
        self.runOutside("cp /etc/resolv.conf %s/etc/." % self.root)
        self.runOutside("cp /etc/localtime %s/etc/." % self.root)
        self.mknods()
        self.dbus()
        self.certificates()
        
    def dbus(self):
        self.runOutside("mkdir -p %s/usr/lib/dbus-1.0/" % self.root)
        self.runOutside("cp /usr/lib/dbus-1.0/dbus-daemon-launch-helper %s/usr/lib/dbus-1.0/." % self.root)
        self.runCommand("groupadd -g 18 messagebus")
        self.runCommand('useradd -m -d /var/run/dbus -r -s /bin/false -u 18 -g 18 messagebus -c "D-Bus Message Daemon"')
        self.runCommand("dbus-uuidgen --ensure")
        self.runCommand("dbus-daemon --system")
        self.runCommand("chmod o+x /usr/lib/dbus-1.0/dbus-daemon-launch-helper")
            
    def mknods(self):
         self.runCommand("mknod /dev/console c 5 1")
         self.runCommand("mknod /dev/null c 1 3")
         self.runCommand("mknod /dev/random c 1 8")
         self.runCommand("mknod /dev/urandom c 1 9")
         self.runCommand("mkdir -p /dev/pts")
         self.runCommand("mknod /dev/pts/0 c 136 0")
         self.runCommand("mknod /dev/pts/1 c 136 1")
         self.runCommand("mknod /dev/pts/2 c 136 2")
         self.runCommand("mknod /dev/pts/3 c 136 3")
         
    def certificates(self):
         self.runCommand("/usr/sbin/update-ca-certificates")

    def runOutside(self, cmd, pisilog = False):
        x = os.popen(cmd,"r").readlines()
        if pisilog == True:
            self.pisilog.mesaj("chroot disinda calisacak : (%s) " % cmd)
            self.pisilog.mesaj(x)
        else:
            self.rootlog.mesaj("chroot disinda calisacak : (%s) " % cmd)
            self.rootlog.mesaj(x)

    def mountDirs(self, umount = False):
        if umount == False:
            for m in self.mounts:
                self.runOutside("mkdir -p %s%s" % (self.root, m))
                self.runOutside("mount --bind %s %s%s" % (m, self.root, m))
        else:
            for m in self.mounts:
                self.runOutside("umount %s%s" % (self.root, m))

    def runCommand(self, cmd, pisilog = False):
        cmd = "chroot %s %s" % (self.root, cmd)
        x = os.popen(cmd,"r").readlines()
        if pisilog == True:
            self.pisilog.mesaj("chroot icinde calisacak : (%s) " % cmd)
            self.pisilog.mesaj(x)
        else:
            self.rootlog.mesaj("chroot icinde calisacak : (%s) " % cmd)
            self.rootlog.mesaj(x)
            
    def installPackages(self, paketListesi):
        for paket in open(paketListesi).readlines():
            Paket(paket, self.root)
        Busybox("paket/busybox-1.22.1-4-p01-x86_64.pisi", self.root)

    def addRepo(self,name, url):
        self.runCommand("pisi ar %s %s" % (name, url))

    def buildpkg(self, pkgname):
        os.system("chroot %s pisi -y  --ignore-safety bi %s" % (self.root,pkgname))
        
if (__name__ == "__main__"):
    x = Chroot(sys.argv[1], sys.argv[2])
    x.addRepo("farm", "http://farm.pisilinux.org/.nofarm-repo/x86_64/pisi-index.xml.xz")
    x.addRepo("source","https://github.com/pisilinux/PisiLinux/raw/master/pisi-index.xml.xz")
    x.buildpkg(sys.argv[3])
             

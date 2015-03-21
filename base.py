import os, sys
from kayit import *

ROOTFS=sys.argv[1]
liste = open("paketler.txt").readlines()
CACHE = "paket"

class Indexes:
    def __init__(self):
        self.indexes = {}
        self.priority = None

    def setPriority(self, reponame):
        self.priority = reponame

    def addIndex(self, index):
        self.indexes[index.name]  = index

    def package(self, name):
        selected = 0
        pkg = None
        repo = ""
        if self.priority != None:
            n = self.priority
            if name in self.indexes[n].packages.keys():
                return (n, self.indexes[n].packages[name])

        for reponame, index in self.indexes.items():
            if name in index.packages.keys():
                if index.packages[name].release > selected:
                    pkg = index.packages[name]
                    selected = pkg.release
                    repo = reponame
        return (repo, pkg)

class Index:
    def __init__(self, name, repo):
        self.url = repo
        self.name = name
        self.base = repo[:repo.rfind("/")+1]
        self.content = ""
        self.packages = {}
        self.checkHash()
        try:
            self.content = open("%s.pisi-index.xml" % self.name).read()
        except:
            self.retrieve()
        self.parse()

    def checkHash(self):
        import urllib2
        if os.path.exists("%s.index.sha1sum" % self.name):
            yeniHash = urllib2.urlopen("%s.sha1sum" % self.url).readlines()[0]
            eskiHash = open("%s.index.sha1sum" % self.name).readlines()[0]
            if yeniHash.strip() != eskiHash.strip():
                self.retrieve()
                f = open("%s.index.sha1sum" % self.name,"w")
                f.write(yeniHash)
                f.close()
            else:
                if not (os.path.exists("%s.pisi-index.xml" % self.name)):
                    self.retrieve()
        else:
            yeniHash = urllib2.urlopen("%s.sha1sum" % self.url).readlines()[0]
            self.retrieve()
            f = open("%s.index.sha1sum" % self.name,"w")
            f.write(yeniHash)
            f.close()



    def retrieve(self):
        os.system("wget %s -O %s.pisi-index.xml.xz" % (self.url, self.name))
        os.system("xz -d %s.pisi-index.xml.xz" % self.name)

    def parse(self):
        from lxml import objectify as obj
        tree = obj.fromstring(self.content)
        for c in tree.getchildren():
            if c.tag == "Package":
                for d in c.getchildren():
                    if d.tag == "Name":
                        pname = d.text
                        self.packages[pname] = Pkg(self.base, pname)
                    if d.tag == "PackageURI":
                        self.packages[pname].setFilename(d.text)
                    if d.tag == "History":
                        found = False
                        for e in d.getchildren():
                            if found == True:
                                break
                            if e.tag == "Update":
                                self.packages[pname].setRelease(int(e.attrib["release"]))
                                found = True
                    if d.tag == "DeltaPackages":
                        for e in d.getchildren():
                            if e.tag == "Delta":
                                for f in e.getchildren():
                                    if f.tag == "PackageURI":
                                        self.packages[pname].addDelta(f.text)

    def report(self):
        for pname, pkg in self.packages.items():
            print "--------  ", pname, "  ----------------"
            print pkg.filename
            for p in pkg.deltas:
                print "      ", p
            print "-----------------------------------------"

class Pkg:
    def __init__(self, base, pname):
        self.name = pname
        self.base = base
        self.filename = ""
        self.release = -1
        self.deltas = []
        self.fname = self.filename.split("/")[-1]

    def report(self):
        print self.name
        print self.filename
        print "Deltas"
        for i in self.deltas:
            print "  ", i

    def setRelease(self, release):
        self.release = release

    def setFilename(self, name):
        self.filename = name
        self.fname = name.split("/")[-1]

    def addDelta(self, delta):
        if len(self.deltas) == 0:
            self.deltas.append(delta)
        elif delta not in self.deltas:
            self.deltas.append(delta)

    def fetch(self):
        if not os.path.exists("%s/%s"  % (CACHE, self.fname)):
            cmd = "wget -c %s/%s -O %s/%s" % (self.base, self.filename, CACHE, self.fname)
            os.system(cmd)

    def install(self, target, withPisi = False):
        self.fetch()
        if withPisi == False:
            p = Paket(self.fname, target)
            for dlt in self.deltas:
                d = dlt.split("/")[-1]
                if not os.path.exists("%s/%s" % (CACHE, d)):
                    cmd = "wget %s/%s -O %s/%s" % (self.base, dlt, CACHE, d)
                    os.system(cmd)
                    p = Paket(d, target)
        else:
            cmd = "pisi it --ignore-safety --ignore-dependency --ignore-comar  -D %s -y %s/%s" \
                  % (target, "%s/%s" % (CACHE, d))

class Paket:
    def __init__(self, dosya_adi,  target):
        self.adi = dosya_adi
        self.unzip(target)
        self.clean()

    def unzip(self, target):
        os.system("unzip  %s/%s " % (CACHE, self.adi))
        os.system("cd %s; tar Jxf ../install.tar.xz" % target)

    def clean(self):
        os.system("rm -rf comar; rm -f install.tar.xz; rm -f files.xml metadata.xml")

class Chroot:
    def __init__(self, dizin, paketListesi, index):
        self.index = index
        self.pisilog = Kayit("%s-pisi.log" % dizin)
        self.rootlog = Kayit("%s-root.log" % dizin)
        self.buildlog = Kayit("%s-build.log" % dizin)
        self.runOutside("rm -rf %s" % dizin)
        self.runOutside("mkdir -p %s/root" % dizin)
        self.root = dizin
        self.mounts = ["/proc", "/sys"]
        self.mountDirs()
        self.liste = liste
        self.installPackages(paketListesi)
        self.runOutside("cp %s/usr/share/baselayout/* %s/etc/." % (self.root, self.root))
        self.runCommand("/sbin/ldconfig")
        self.runCommand("/sbin/update-environment")

        self.runOutside("cp /etc/resolv.conf %s/etc/." % self.root)
        self.runOutside("cp /etc/localtime %s/etc/." % self.root)
        self.mknods()
        self.dbus()
        self.certificates()
        self.runOutside("mkdir -p %s/var/cache/pisi/packages/" % self.root)
        self.runOutside("cp %s/* %s/var/cache/pisi/packages/" % (CACHE, self.root))


    def installWithPisi(self):
        for p in self.liste:
            p = p.strip()
            repo, pkg = self.index.package(p)
            fname = pkg.filename.split("/")[-1]
            cmd = "pisi --ignore-safety --ignore-dependency --ignore-comar -y it  /var/cache/pisi/packages/%s" % fname
            self.runCommand(cmd)

    def cleanDocs(self):
        if self.root !="":
            self.runOutside("rm -rf %s/usr/share/man" % self.root)
            self.runOutside("rm -rf %s/usr/share/doc" % self.root)
            self.runOutside("rm -rf %s/usr/share/gtk-doc" % self.root)
            self.runOutside("rm -rf %s/usr/share/locale/[a-d][f-z]*" % self.root)
            self.runOutside("rm -rf %s/usr/share/locale/e[a-m,o-z]*" % self.root)
            self.runCommand("rm -rf /var/cache/pisi/packages/*")
            self.runCommand("rm -rf /var/cache/pisi/archives/*")
            self.runCommand("rm -rf /var/run/dbus/pid")


    def dbus(self):
        #self.runOutside("mkdir -p %s/usr/lib/dbus-1.0/" % self.root)
        #self.runOutside("cp /usr/lib/dbus-1.0/dbus-daemon-launch-helper %s/usr/lib/dbus-1.0/." % self.root)
        #self.runCommand("groupadd -g 18 messagebus")

        if not os.path.exists("%s/var/lib/dbus/machine-id" % self.root):
            self.runCommand("dbus-uuidgen --ensure")

        self.runCommand("/sbin/start-stop-daemon -b --start  --pidfile /var/run/dbus/pid --exec /usr/bin/dbus-daemon -- --system")

        #self.runCommand('useradd -m -d /var/run/dbus -r -s /bin/false -u 18 -g 18 messagebus -c "D-Bus Message Daemon"')
        #self.runCommand("dbus-daemon --system")
        #self.runCommand("chmod o+x /usr/lib/dbus-1.0/dbus-daemon-launch-helper")

    def mknods(self):
        self.runCommand("mkdir -m 755 -p /dev/pts")
        self.runCommand("mknod -m 666 /dev/null c 1 3")
        self.runCommand("mknod -m 666 /dev/zero c 1 5")
        self.runCommand("mknod -m 666 /dev/random c 1 8")
        self.runCommand("mknod -m 666 /dev/urandom c 1 9")
        self.runCommand("mkdir -m 1777 /dev/shm")
        self.runCommand("mknod -m 666 /dev/tty c 5 0")
        self.runCommand("mknod -m 600 /dev/console c 5 1")
        self.runCommand("mknod -m 666 /dev/tty0 c 5 0")
        self.runCommand("mknod -m 666 /dev/full c 1 7")
        self.runCommand("mknod -m 600 /dev/initctl p")
        self.runCommand("mknod -m 666 /dev/ptmx c 5 2")
        for i in range(255):
            self.runCommand("mknod /dev/pts/%d c 136 %d" % (i,i))
        self.runOutside("ln -sf /proc/self/fd %s/dev/fd" % self.root)

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
            paket = paket.strip()
            repo, pkg = self.index.package(paket)
            print "%s reposundan %s kuruluyor" % (repo, paket)
            pkg.install(self.root)

    def addRepo(self,name, url):
        self.runCommand("pisi ar %s %s" % (name, url))

    def buildpkg(self, pkgname):
        self.runCommand("pisi -y  --ignore-safety bi %s" % pkgname)

    def docker(self):
        arch = "x86_64"
        img = "pisichroot"
        release = logtime().replace(":","").replace("-","")
        imgtag = "%s-%s-%s" % (img ,arch, release)
        self.mountDirs(True)
        self.cleanDocs()
        dockercmd = "tar --numeric-owner --xattrs --acls -C %s -c .  | docker import - %s " % (self.root, imgtag)
        tagcmd = "docker tag -f %s %s:latest" % (imgtag, img)
        self.runOutside(dockercmd)
        self.runOutside(tagcmd)

if (__name__ == "__main__"):
    os.system("mkdir -p %s" % CACHE)
    I = Index("farm","http://farm.pisilinux.org/.nofarm-repo/x86_64/pisi-index.xml.xz")
    J = Index("ilker","http://manap.se/pisi/pisi-index.xml.xz")
    K = Indexes()
    K.addIndex(I)
    K.addIndex(J)
    K.setPriority("ilker")
    x = Chroot(sys.argv[1], sys.argv[2], K)

    x.addRepo("farm", "http://farm.pisilinux.org/.nofarm-repo/x86_64/pisi-index.xml.xz")
    x.addRepo("ilker", "http://manap.se/pisi/pisi-index.xml.xz")

    x.addRepo("source","https://github.com/ertugerata/PisiLinux/raw/Pisi-2.0/pisi-index.xml.xz")
    x.runCommand("pisi dr farm")
    x.installWithPisi()
    #x.addRepo("source","/home/ertugrul/Works/PisiLinux/pisi-index.xml.xz")
    #x.buildpkg(sys.argv[3])
    #x.docker()

import os
from base import *

os.system("mkdir -p %s" % CACHE)
J = Index("ilker","http://manap.se/pisi/pisi-index.xml.xz")
K = Indexes()
K.addIndex(J)
K.setPriority("ilker")

x = Docker(sys.argv[1], BASE, K)
#x.addRepo("farm", "http://farm.pisilinux.org/.nofarm-repo/x86_64/pisi-index.xml.xz",2)
#x.addRepo("ilker", "http://manap.se/pisi/pisi-index.xml.xz")
#x.addRepo("source","https://github.com/ertugerata/PisiLinux/raw/Pisi-2.0/pisi-index.xml.xz")
x.installWithPisi()
x.dockerImport("pisichroottest")

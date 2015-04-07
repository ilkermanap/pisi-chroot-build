import os, sys

def dockerInstall():
    """
    Docker check function.
    If not found, it will build the pisi package from
    github repo, and install it.

    If everything is ok, the function will return 0
    If build fails, it will return 1,
    If install fails, it will return 2
    If running user is not root, it will return 4
    """
    if os.getuid() != 0:
        print "These functions requires root access, run the application with sudo"
        return 4
    ret = -1
    status = os.system("which docker >/dev/null")
    if status != 0:
        pspec = "https://raw.githubusercontent.com/ertugerata/ertugerata_playground/master/docker/pspec.xml"
        cmd = "pisi bi -y %s" % pspec
        buildstat = os.system(cmd)
        if buildstat == 0:
            cmd = "pisi it docker*.pisi"
            installstat = os.system(cmd)
            if installstat != 0:
                print "Package installation failed"
                ret += 2
        else:
            print "Building docker failed"
            ret += 1
    else:
        ret = 0
    return ret


class Container:
    def __init__(self, repo, tag, imageid, created, virtsize):
        self.repo = repo
        self.tag = tag
        self.imageid = imageid
        self.created = created
        self.size = virtsize
        os.system("docker run %s" % self.repo)

    def runCommand(self, command):
        cmd = "docker exec %s %s " % (self.repo, command)
        print "starting ",  cmd
        ans = os.popen(cmd).read()
        print "finished ",  cmd
        return ans

    def info(self):
        return """
Repository  : %s
Tag         : %s
Image Id    : %s
Created     : %s 
Virtual Size: %s""" % (self.repo, self.tag, self.imageid, self.created, self.size)

class DockerModule:
    def __init__(self):
        state = dockerInstall()
        if state == 0:
            pass
        else:
            print "Problem with docker installation, exiting"
            sys.exit()
        state = os.system("docker images 2> /dev/null 1>/dev/null")
        if state != 0:
            print "Starting docker daemon"
            self.startDocker()

        self.info = {}
        self.images = {}
        self.imageList()

    def getInfo(self):
        cmd = "docker info"
        answer = os.popen(cmd, "r").readlines()
        for line in answer:
            if line.find("INFO[") > -1:
                pass
            l = line.strip()
            fields = l.split(":")
            if fields[0] == "ID":
                self.info["ID"] = l[3:].strip()
            else:
                self.info[fields[0]] = fields[1]

    def imageList(self):
        cmd = "docker images"
        ans = os.popen(cmd,"r").readlines()
        header = ans[0]
        tagst = header.find("TAG")
        imst = header.find("IMAGE ID")
        crst = header.find("CREATED")
        vrst = header.find("VIRTUAL SIZE")
        for l in ans[1:]:
            repo = l[:tagst].strip()
            tag  = l[tagst:imst].strip()
            imageid = l[imst:crst].strip()
            created = l[crst:vrst].strip()
            virtsize = l[vrst:].strip()
            self.images[repo] = Container(repo, tag, imageid, created, virtsize)

    def startDocker(self):
        print "starting docker"
        os.system("cgroupfs-mount")
        os.system("docker -d 2>/dev/null 1>/dev/null&")


if __name__ == "__main__":
    x = DockerModule()

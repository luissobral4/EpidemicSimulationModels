import simian
from simian import Simian
import random, math, argparse, textwrap



parser = argparse.ArgumentParser(
    description='The PHOLD model.',
    formatter_class=argparse.RawDescriptionHelpFormatter)

parser.add_argument('total_nodes', metavar='NNODES', type=int,
                    help='total number of nodes')
parser.add_argument('endtime', metavar='ENDTIME', type=float,
                    help='simulation end time')
parser.add_argument("-d", "--distance", type=float, metavar='DISTANCE', default=100.0,
                    help="maximum distance to be neighbors")
parser.add_argument("-l", "--lookahead", type=float, metavar='LOOKAHEAD', default=0.1,
                    help="min delay of mailboxes")
parser.add_argument("--seedR", type=int, metavar='SEED', default=10,
                    help="seed for random")
parser.add_argument("--useMPI", type=int, metavar='MPI', default=0,
                    help="use mpi")
args = parser.parse_args()

uMPI = False
if args.useMPI == 1:
    uMPI = True
nodes = args.total_nodes
lookahead = args.lookahead

simName, startTime, endTime, minDelay, useMPI, mpiLib =  str(args.total_nodes), 0, args.endtime, args.lookahead, uMPI, "/usr/lib/x86_64-linux-gnu/libmpich.so"
simianEngine = Simian(simName, startTime, endTime, minDelay, useMPI)

timeout1 = 1
timeout2 = 2
random.seed(args.seedR)

# Init grid
positions = []
# Place nodes in grids
for x in range(int(math.sqrt(nodes))):
    for y in range(int(math.sqrt(nodes))):
        px = 50 + x*60 + random.uniform(-20,20)
        py = 50 + y*60 + random.uniform(-20,20)
        positions.append((px,py))

class msg2:
    def __init__(self,type,m,mID,round,sender):
        self.type = type
        self.payload = m
        self.ID = int(mID)
        self.round = int(round)
        self.sender = int(sender)

class Node(simianEngine.Entity):
    def __init__(self, baseInfo, *args):
        super(Node, self).__init__(baseInfo)
        self.total_nodes = args[1]
        self.node_idx = args[0]
        self.eagerPushPeers = []
        self.lazyPushPeers = []
        self.lazyQueues = []
        self.missing = []
        self.receivedMsgs = {}
        self.timers = {}
        self.GetPeers()

    def Receive(self, *args):
        m = args[0]
        m2 = m.split("-")
        msg = msg2(m2[0],m2[1],m2[2],m2[3],m2[4])
        #self.out.write(str(self.engine.now) + (":%d rcvd msg '%s' %d\n" % (self.node_idx, msg.type,msg.sender)))
        if msg.type =='PRUNE':
            if msg.sender in self.eagerPushPeers:
                self.eagerPushPeers.remove(msg.sender)
            if msg.sender not in self.lazyPushPeers:
                self.lazyPushPeers.append(msg.sender)
        elif msg.type =='IHAVE':
            if msg.ID not in self.receivedMsgs.keys():
                self.missing.append((msg.ID,msg.sender,msg.round))
                # setup timer
                if msg.ID not in self.timers.keys():
                    self.timers[msg.ID] = 1
                    self.reqService(lookahead, "Timer", msg.ID)

        elif msg.type =='GRAFT':
            if msg.sender not in self.eagerPushPeers:
                self.eagerPushPeers.append(msg.sender)
            if msg.sender in self.lazyPushPeers:
                self.lazyPushPeers.remove(msg.sender)
            if msg.ID in self.receivedMsgs.keys():
                msend = ('GOSSIP-'+self.receivedMsgs[msg.ID]+'-'+str(msg.ID)+'-'+str(msg.round)+'-'+str(self.node_idx))
                self.reqService(lookahead, "Receive", msend, "Node", msg.sender)

        elif msg.type =='GOSSIP':
            if msg.ID not in self.receivedMsgs.keys():
                self.receivedMsgs[msg.ID] = msg.payload

                if msg.ID in self.timers.keys():
                    self.timers.pop(msg.ID)

                self.LazyPush(msg)
                self.EagerPush(msg)

                if msg.sender not in self.eagerPushPeers:
                    self.eagerPushPeers.append(msg.sender)
                if msg.sender in self.lazyPushPeers:
                    self.lazyPushPeers.remove(msg.sender)
            else:
                if msg.sender in self.eagerPushPeers:
                    self.eagerPushPeers.remove(msg.sender)
                if msg.sender not in self.lazyPushPeers:
                    self.lazyPushPeers.append(msg.sender)

                self.reqService(lookahead, "Receive", ('PRUNE--0-0-'+str(self.node_idx)), "Node", msg.sender)

        elif msg.type =='BROADCAST':
            mID = msg.ID
            self.EagerPush(msg)
            self.LazyPush(msg)
            self.receivedMsgs[mID] = msg.payload


    def EagerPush(self, msg):
        msg2 = ('GOSSIP-'+msg.payload+'-'+str(msg.ID)+'-'+str(msg.round+1)+'-'+str(self.node_idx))
        sender = msg.sender
        c = 0
        for n in self.eagerPushPeers:
            if n != self.node_idx:
                c+=1
                self.reqService(lookahead * c, "Receive", msg2, "Node", n)

    def LazyPush(self, msg):
        m = 'IHAVE-'+""+'-'+str(msg.ID)+'-'+str(msg.round+1)+'-'+str(self.node_idx)
        sender = msg.sender
        for n in self.lazyPushPeers:
            if n != self.node_idx:
                self.reqService(lookahead, "Receive", m, "Node", n)

    def GetPeers(self):
        lsize = int(math.sqrt(args.total_nodes))
        idx = self.node_idx
        xp = idx // lsize
        yp = idx % lsize

        rxmin = xp - 2
        rxmax = xp + 2
        rymin = yp - 2
        rymax = yp + 2

        if rxmin < 0:
            rxmin = 0
        if rxmax > lsize:
            rxmax = lsize
        if rymin < 0:
            rymin = 0
        if rymax > lsize:
            rymax = lsize

        for x in range(rxmin,rxmax):
            for y in range(rymin,rymax):
                peer = (x * lsize) + y
                v1 = positions[self.node_idx][0]-positions[peer][0]
                v2 = positions[self.node_idx][1]-positions[peer][1]
                dist = math.sqrt(v1*v1 + v2*v2)
                if peer!=self.node_idx and dist<args.distance:
                    self.eagerPushPeers.append(peer)

    def Timer(self,*args):
        mID = args[0]
        # if mID not in self.timers.keys():
        #     print('timer cancelled!')

        #else:
        if mID in self.timers.keys():
            #print(str(self.engine.now)+"--------started timer for mID:"+str(mID)+" on node "+str(self.node_idx))
            m = (mID,0,0)
            for p in self.missing:
                if p[0] == mID:
                    m = p
                    self.missing.remove(p)

            if m[1] not in self.eagerPushPeers:
                self.eagerPushPeers.append(m[1])
            if m[1] in self.lazyPushPeers:
                self.lazyPushPeers.remove(m[1])

            msg = 'GRAFT--'+str(mID)+'-'+str(m[2])+'-'+str(self.node_idx)
            self.reqService(lookahead, "Receive", msg, "Node", m[1])

            self.reqService(timeout2, "Timer", mID)

for i in range(nodes):
    simianEngine.addEntity("Node", Node, i,i,nodes)

#for i in range(endTime):
#idx = random.randrange(nodes)
msgID = 1
for i in range(int(args.endtime/10)):
    idx = random.randrange(nodes)
    delay = lookahead
    simianEngine.schedService(lookahead + i*10, "Receive", 'BROADCAST-hello-%d-0-0'%msgID, "Node", idx)
    msgID+=1

#simianEngine.schedService(10, "Receive", 'BROADCAST-hello-%d-0-0'%2, "Node", idx)

simianEngine.run()
simianEngine.exit()

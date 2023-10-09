import simulus, random, argparse, textwrap, math, time

st = time.time()
def BLOCK_LOW(id,p,n): return int(id*n/p)
def BLOCK_HIGH(id,p,n): return BLOCK_LOW(id+1,p,n)-1
def BLOCK_SIZE(id,p,n): return BLOCK_LOW(id+1)-BLOCK_LOW(id)
def BLOCK_OWNER(index,p,n): return int((p*(index+1)-1)/n)

timeout1 = 1
timeout2 = 2

class msg2:
    def __init__(self,type,m,mID,round,sender):
        self.type = type
        self.payload = m
        self.ID = int(mID)
        self.round = int(round)
        self.sender = int(sender)

class node(object):
    def __init__(self, sim, idx,total_nodes,lookahead):
        self.lookahead = lookahead
        self.sim = sim
        self.total_nodes = total_nodes
        self.node_idx = idx
        self.eagerPushPeers = []
        self.lazyPushPeers = []
        self.lazyQueues = []
        self.missing = []
        self.receivedMsgs = {}
        self.timers = {}
        self.mbox = sim.mailbox(name='mb%d'%idx, min_delay=lookahead)
        sim.process(self.receive)

    def eagerPush(self,msg, mID, round, sender):
        c = 0
        for n in self.eagerPushPeers:
            #delay = self.sim.rng().expovariate(1)+self.lookahead
            delay = self.lookahead
            if n != sender:
                c+=1
                self.sim.sync().send(self.sim, 'mb%d'% n, ('GOSSIP-'+msg+'-'+str(mID)+'-'+str(round)+'-'+str(self.node_idx)),delay*c)

    def lazyPush(self,msg, mID, round, sender):
        for n in self.lazyPushPeers:
            if n != sender:
                #delay = self.sim.rng().expovariate(1)+self.lookahead
                delay = self.lookahead
                m = 'IHAVE-'+""+'-'+str(mID)+'-'+str(round)+'-'+str(self.node_idx)
                self.sim.sync().send(self.sim, 'mb%d'% n, m,delay)

    def msg(type,m,mID,round,sender):
        return "%s-%s-%d-%d-%d"%(type,m,mID,round,sender)

    def receive(self):
        self.eagerPushPeers = self.getPeers()
        v = 1
        while v == 1:
            m = self.mbox.recv(isall=False)
            m2 = m.split("-")
            msg = msg2(m2[0],m2[1],m2[2],m2[3],m2[4])
            print("%g: '%s' rcvd msg '%s' %d round:%d" % (self.sim.now, self.sim.name, msg.type,msg.sender,msg.round))
            if msg.type =='PRUNE':
                if msg.sender in self.eagerPushPeers:
                    self.eagerPushPeers.remove(msg.sender)
                if msg.sender not in self.lazyPushPeers:
                    self.lazyPushPeers.append(msg.sender)

            elif msg.type =='IHAVE':
                if msg.ID not in self.receivedMsgs.keys():
                    # setup timer
                    self.missing.append((msg.ID,msg.sender,msg.round))
                    if msg.ID not in self.timers.keys():
                        self.timers[msg.ID] = self.sim.sched(self.timer,until=self.sim.now+self.lookahead,mID=msg.ID)


            elif msg.type =='GRAFT':
                if msg.sender not in self.eagerPushPeers:
                    self.eagerPushPeers.append(msg.sender)
                if msg.sender in self.lazyPushPeers:
                    self.lazyPushPeers.remove(msg.sender)
                if msg.ID in self.receivedMsgs.keys():
                    #delay = self.sim.rng().expovariate(1)+self.lookahead
                    delay = self.lookahead
                    msgS = ('GOSSIP-'+self.receivedMsgs[msg.ID]+'-'+str(msg.ID)+'-'+str(msg.round)+'-'+str(self.node_idx))
                    self.sim.sync().send(self.sim, 'mb%d'% msg.sender, msgS,delay)

            elif msg.type =='GOSSIP':
                if msg.ID not in self.receivedMsgs.keys():
                    self.receivedMsgs[msg.ID] = msg.payload

                    if msg.ID in self.timers.keys():
                        #print("timer cancel")
                        self.sim.cancel(self.timers[msg.ID])
                        self.timers.pop(msg.ID)

                    self.eagerPush(msg.payload,msg.ID,msg.round+1,self.node_idx)
                    self.lazyPush(msg.payload,msg.ID,msg.round+1,self.node_idx)

                    if msg.sender not in self.eagerPushPeers:
                        self.eagerPushPeers.append(msg.sender)
                    if msg.sender in self.lazyPushPeers:
                        self.lazyPushPeers.remove(msg.sender)
                else:
                    if msg.sender in self.eagerPushPeers:
                        self.eagerPushPeers.remove(msg.sender)
                    if msg.sender not in self.lazyPushPeers:
                        self.lazyPushPeers.append(msg.sender)
                    #delay = self.sim.rng().expovariate(1)+self.lookahead
                    delay = self.lookahead
                    self.sim.sync().send(self.sim, 'mb%d'% msg.sender, ('PRUNE--0-0-'+str(self.node_idx)),delay)

            elif msg.type =='BROADCAST':
                mID = msg.ID
                self.eagerPush(msg.payload,mID,0,self.node_idx)
                self.lazyPush(msg.payload,mID,0,self.node_idx)
                self.receivedMsgs[mID] = msg.payload

    def timer(self,**args):
        mID = args["mID"]
        #print(str(self.sim.now)+"------started timer for mID:"+str(mID)+" on node "+str(self.node_idx))
        m = (mID,0,0)
        for p in self.missing:
            if p[0] == mID:
                m = p
                self.missing.remove(p)
        if m[1] not in self.eagerPushPeers:
            self.eagerPushPeers.append(m[1])
        if m[1] in self.lazyPushPeers:
            self.lazyPushPeers.remove(m[1])
        #delay = self.sim.rng().expovariate(1)+self.lookahead
        delay = self.lookahead
        msg = ('GRAFT--'+str(mID)+'-'+str(m[2])+'-'+str(self.node_idx))
        self.sim.sync().send(self.sim, 'mb%d'% m[1], msg,delay)
        self.timers[mID] = self.sim.sched(self.timer,**args, offset=timeout2)

    def getPeers(self):
        neighbors_list=[]
        lsize = int(math.sqrt(self.total_nodes))
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
                if peer!=idx and self.distance(peer)<args.distance:
                    neighbors_list.append(peer)

        # for x in range(self.total_nodes):
        #     if x!=self.node_idx and self.distance(x)<args.distance:
        #         neighbors_list.append(x)
        return neighbors_list

    def distance(self,idx):
        return math.sqrt((positions[self.node_idx][0]-positions[idx][0])*
                        (positions[self.node_idx][0]-positions[idx][0]) +
                        (positions[self.node_idx][1]-positions[idx][1])*
                        (positions[self.node_idx][1]-positions[idx][1])
                        )

# get the total number of processes used to run the simulation (psize)
# as well as the rank of this process (rank), assuming that we are
# using MPI to run this code; if not, rank will be zero and psize will
# be one
rank = simulus.sync.comm_rank()   # process rank
psize = simulus.sync.comm_size()  # total processes

# parsing the command line; the optional arguments used by simulus
# have already been filtered out by simulus when simulus is imported
parser = argparse.ArgumentParser(
    parents=[simulus.parser], # allow -h or --help to show simulus arguments
    description='The PHOLD model.',
    formatter_class=argparse.RawDescriptionHelpFormatter,
    epilog=textwrap.dedent('''\
        CHOICE (-c or --choice) can be any of the following:
          1: sequential simulation (default)
          2: parallel simulation on shared-memory multiprocessors
          3: parallel simulation using mpi
          4: parallel simulation with mpi and multiprocessing
    '''))
parser.add_argument('total_nodes', metavar='NNODES', type=int,
                    help='total number of nodes')
parser.add_argument('endtime', metavar='ENDTIME', type=float,
                    help='simulation end time')
parser.add_argument("-m", "--nsims", type=int, metavar='NSIMS', default=None,
                    help="total number of simulators")
parser.add_argument("-c", "--choice", type=int, metavar='CHOICE', default=1,
                    help="choose simulation method (see below)")
parser.add_argument("--seedR", type=int, metavar='SEED', default=10,
                    help="seed for random")
parser.add_argument("-l", "--lookahead", type=float, metavar='LOOKAHEAD', default=0.1,
                    help="min delay of mailboxes")
parser.add_argument("-d", "--distance", type=float, metavar='DISTANCE', default=100.0,
                    help="maximum distance to be neighbors")

args = parser.parse_args()
if args.nsims is None:
    args.nsims = args.total_nodes
elif args.nsims < psize or args.nsims > args.total_nodes:
    raise ValueError('nsims must be an integer between PSIZE (%d) and NNODES (%d)' %
                     (psize, args.total_nodes))

if rank == 0:
    print('> MODEL PARAMETERS:')
    print('>> TOTAL NODES:', args.total_nodes)
    print('>> LOOKAHEAD:', args.lookahead)
    print('>> CHOICE:', args.choice)
    print('>> TOTAL SIMS: ', args.nsims)
    print('>> END TIME: ', args.endtime)
    print('>> TOTAL SPMD PROCESSES:', psize)

nodes=[]
# create simulators and nodes
sims = [] # all simulators instantiated on this machine
for s in range(BLOCK_LOW(rank, psize, args.nsims), BLOCK_LOW(rank+1, psize, args.nsims)):
    sim = simulus.simulator(name='sim%d'%s)
    sims.append(sim)
    #print('[%d] creating simulator %s...' % (rank, sim.name))

    for idx in range(BLOCK_LOW(s, args.nsims, args.total_nodes),
                     BLOCK_LOW(s+1, args.nsims, args.total_nodes)):
        #print('[%d]  creating node %d...' % (rank, idx))
        nodes.append(node(sim, idx, args.total_nodes,args.lookahead))

if args.choice == 1:
    # case 1: sequential simulation
    if psize > 1:
        raise RuntimeError("You are running MPI; consider CHOICE 3 or 4.")
    syn = simulus.sync(sims)
elif args.choice == 2:
    # case 2: parallel simulation on shared-memory multiprocessors
    if psize > 1:
        raise RuntimeError("You are running MPI; consider CHOICE 3 or 4.")
    syn = simulus.sync(sims, enable_smp=True)
elif args.choice == 3:
    # case 3: parallel simulation with mpi
    syn = simulus.sync(sims, enable_spmd=True)
elif args.choice == 4:
    # case 4: parallel simulation with mpi and multiprocessing
    syn = simulus.sync(sims, enable_smp=True, enable_spmd=True)
else:
    raise ValueError("CHOICE (%d) should be 1-4" % choice)

# Init grid
positions = []
random.seed(args.seedR)
# Place nodes in grids
for x in range(int(math.sqrt(args.total_nodes))):
    for y in range(int(math.sqrt(args.total_nodes))):
        px = 50 + x*60 + random.uniform(-20,20)
        py = 50 + y*60 + random.uniform(-20,20)
        positions.append((px,py))

if rank > 0:
    # only run() without parameters is allowed for higher ranks
    syn.run()
else:
    msgID = 1
    for i in range(int(args.endtime/10)):
        idx = random.randrange(len(nodes))
        delay = args.lookahead
        syn.send(sims[idx], 'mb%d'% idx, 'BROADCAST-hello-%d-0-0'%msgID,delay + i * 10)
        msgID+=1
        #time.sleep(10)
    #syn.send(sims[idx], 'mb%d'% idx, 'BROADCAST-hello-%d-0-0'%2,10)

    # run simulation and get runtime performance report
    syn.run(args.endtime)
    et = time.time()
    syn.show_runtime_report(prefix='>')
    print('>execution time python:', et - st)

#timeout values
#lookahead
#ver delays
#solucao para lazy push
#peer sampling service
#gerar msg id

import simpy,random, argparse, textwrap, math, time
from functools import partial, wraps

st = time.time()
timeout1 = 1
timeout2 = 2
events = 0

class msg2:
    def __init__(self,type,m,mID,round,sender):
        self.type = type
        self.payload = m
        self.ID = int(mID)
        self.round = int(round)
        self.sender = int(sender)

class Node(object):
    def __init__(self, env, in_pipe, idx, total_nodes,lookahead):
        self.env = env
        self.lookahead = lookahead
        self.total_nodes = total_nodes
        self.node_idx = idx
        self.eagerPushPeers = []
        self.lazyPushPeers = []
        self.lazyQueues = []
        self.missing = []
        self.receivedMsgs = {}
        self.timers = {}

        self.in_pipe = in_pipe
        #self.pipes = []
        self.env.process(self.receive())

    def receive(self):
        self.eagerPushPeers = self.getPeers()
        while True:
            # Get event for message pipe
            m = yield self.in_pipe.get()
            #yield env.timeout(random.randint(1, 2))
            m2 = m.split("-")
            msg = msg2(m2[0],m2[1],m2[2],m2[3],m2[4])
            #print("%g: %d rcvd msg '%s' %d round:%d" % (self.env.now, self.node_idx, msg.type,msg.sender,msg.round))

            if msg.type =='PRUNE':
                #print("%g: %d rcvd msg '%s' %d round:%d" % (self.env.now, self.node_idx, msg.type,msg.sender,msg.round))

                if msg.sender in self.eagerPushPeers:
                    self.eagerPushPeers.remove(msg.sender)
                if msg.sender not in self.lazyPushPeers:
                    self.lazyPushPeers.append(msg.sender)

            elif msg.type =='IHAVE':
                if msg.ID not in self.receivedMsgs.keys():
                    self.missing.append((msg.ID,msg.sender,msg.round))
                    # setup timer
                    if msg.ID not in self.timers.keys():
                        yield env.timeout(self.lookahead)
                        self.timers[msg.ID] = self.env.process(self.timer(msg.ID))

            elif msg.type =='GRAFT':
                if msg.sender not in self.eagerPushPeers:
                    self.eagerPushPeers.append(msg.sender)
                if msg.sender in self.lazyPushPeers:
                    self.lazyPushPeers.remove(msg.sender)
                if msg.ID in self.receivedMsgs.keys():

                    msgS = 'GOSSIP-'+self.receivedMsgs[msg.ID]+'-'+str(msg.ID)+'-'+str(msg.round)+'-'+str(self.node_idx)
                    env.process(self.send(msg.sender,msgS))

            elif msg.type =='GOSSIP':
                if msg.ID not in self.receivedMsgs.keys():
                    self.receivedMsgs[msg.ID] = msg.payload

                    if msg.ID in self.timers.keys():
                        self.timers[msg.ID].interrupt()

                    env.process(self.eagerPush(msg.payload,msg.ID,msg.round+1,self.node_idx))
                    env.process(self.lazyPush(msg.payload,msg.ID,msg.round+1,self.node_idx))

                    if msg.sender not in self.eagerPushPeers:
                        self.eagerPushPeers.append(msg.sender)
                    if msg.sender in self.lazyPushPeers:
                        self.lazyPushPeers.remove(msg.sender)
                else:
                    if msg.sender in self.eagerPushPeers:
                        self.eagerPushPeers.remove(msg.sender)
                    if msg.sender not in self.lazyPushPeers:
                        self.lazyPushPeers.append(msg.sender)

                    msgS = 'PRUNE--0-0-'+str(self.node_idx)
                    env.process(self.send(msg.sender,msgS))


            elif msg.type =='BROADCAST':
                mID = msg.ID
                env.process(self.eagerPush(msg.payload,mID,0,self.node_idx))
                env.process(self.lazyPush(msg.payload,mID,0,self.node_idx))
                self.receivedMsgs[mID] = msg.payload

    def eagerPush(self,msg, mID, round, sender):
        for peer in self.eagerPushPeers:
            yield env.timeout(self.lookahead)
            m = 'GOSSIP-'+msg+'-'+str(mID)+'-'+str(round)+'-'+str(self.node_idx)
            pipes[peer].put(m)

    def send(self,node,msg):
        yield env.timeout(self.lookahead)
        pipes[node].put(msg)

    def lazyPush(self,msg, mID, round, sender):
        for peer in self.lazyPushPeers:
            yield env.timeout(self.lookahead)
            m = 'IHAVE-'+""+'-'+str(mID)+'-'+str(round)+'-'+str(self.node_idx)
            pipes[peer].put(m)

    def timer(self,mID):
        #print(str(env.now)+"--------started timer for mID:"+str(mID)+" on node "+str(self.node_idx))
        #timers[msg.ID] = sim.sched(self.timer(mID), offset=timeout2)
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
        pipes[m[1]].put(msg)

        #schedule new event
        try:
            yield self.env.timeout(timeout2)
            self.timers[mID] = self.env.process(self.timer(mID))
        except simpy.Interrupt:
            self.timers.pop(mID)
            #print('timer cancelled!')

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
        return neighbors_list

    def distance(self,idx):
        return math.sqrt((positions[self.node_idx][0]-positions[idx][0])*
                        (positions[self.node_idx][0]-positions[idx][0]) +
                        (positions[self.node_idx][1]-positions[idx][1])*
                        (positions[self.node_idx][1]-positions[idx][1])
                        )

def delay(env, duration):
    yield env.timeout(duration)

def broadcast(env,t,idx,mID):
    yield env.timeout(t)
    pipes[idx].put('BROADCAST-hello-'+str(mID)+'-0-0')

def trace(env, callback):
     def get_wrapper(env_step, callback):
         @wraps(env_step)
         def tracing_step():
             if len(env._queue):
                 t, prio, eid, event = env._queue[0]
                 callback(t, prio, eid, event)
             return env_step()
         return tracing_step

     env.step = get_wrapper(env.step, callback)


def monitor(data, t, prio, eid, event):
    if isinstance(event,simpy.resources.store.StoreGet):
        data[0] += 1
    elif isinstance(event,simpy.resources.store.StorePut):
        data[1] += 1
    elif isinstance(event,simpy.events.Interruption):
        data[2] += 1
    elif isinstance(event,simpy.events.Timeout):
        data[3] += 1

data = [0,0,0,0]

monitor = partial(monitor, data)

rank = 0   # process rank
psize = 1  # total processes

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
args = parser.parse_args()

if rank == 0:
    print('> MODEL PARAMETERS:')
    print('>> TOTAL NODES:', args.total_nodes)
    print('>> END TIME: ', args.endtime)
    print('>> TOTAL SPMD PROCESSES:', psize)

pipes=[]
nodes=[]
env = simpy.Environment()
trace(env, monitor)

for i in range(args.total_nodes):
    pipes.append(simpy.Store(env))
    nodes.append(Node(env,pipes[i],i,args.total_nodes,args.lookahead))

# Init grid
positions = []
random.seed(args.seedR)
# Place nodes in grids
for x in range(int(math.sqrt(args.total_nodes))):
    for y in range(int(math.sqrt(args.total_nodes))):
        px = 50 + x*60 + random.uniform(-20,20)
        py = 50 + y*60 + random.uniform(-20,20)
        positions.append((px,py))

msgID = 1
for i in range(int(args.endtime/10)):
    idx = random.randrange(len(nodes))
    delay = args.lookahead
    env.process(broadcast(env,delay + i * 10,idx,msgID))
    msgID+=1

# idx = random.randrange(len(nodes))
# env.process(broadcast(env,0,idx,1))
#env.process(broadcast(env,10,idx,2))
# for i in range(int(args.endtime)):
#     idx = random.randrange(len(nodes))
#     env.process(broadcast(env,i,idx,i))

env.run(until=args.endtime)
et = time.time()
print('>> MSGs SENDED:', data[1])
print('>> MSGs RECEIVED:', data[0])
print('>> cancelled events:', data[2])
print('>> executed events:', data[3])
print('>> execution time:', et - st)

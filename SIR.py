import snap
import random 
filename = "soc-Epinions1.txt"
graph = snap.LoadEdgeList(snap.PNGraph, filename, 0, 1)
net = snap.LoadEdgeList(snap.PNEANet, filename, 0, 1)

# Simulate SIR model
# state: 
#   0: susceptible
#   1: infectious
#   2: removed
initial_list = [18, 737, 118, 40, 27, 19, 0, 4, 5, 10, 12, 28, 34, 77, 136 , 1719] #nodes with high page rank
tl = 2 # max step of infection
#init
for NI in net.Nodes():
    nid = NI.GetId()
    state = 0
    if nid in initial_list: 
        state = 1
    else:
        state = 0
    result = net.AddIntAttrDatN(nid, state, "state")
    result = net.AddIntAttrDatN(nid, 0, "step")
#infect
numberNode = net.GetNodes()
numberR = numberNode - len(initial_list)
numberEcho = 0
while numberR != numberNode:
    for NI in net.Nodes():
        nid = NI.GetId()
        if net.GetIntAttrDatN(nid, "state") == 1:
            for connectedNode in NI.GetOutEdges():
                if (random.randint(0, 4) == 0) and (net.GetIntAttrDatN(connectedNode, "state") == 0): 
                    result = net.AddIntAttrDatN(connectedNode, 1, "state")
            
            nowStep = net.GetIntAttrDatN(nid, "step") + 1
            result = net.AddIntAttrDatN(nid, nowStep, "step")
            if nowStep == tl:
                result = net.AddIntAttrDatN(nid, 2, "state")
    tempR = 0
    for NI in net.Nodes():
        nid = NI.GetId()
        if (net.GetIntAttrDatN(nid, "state") == 1):
            break
        elif (net.GetIntAttrDatN(nid, "state") == 0) or (net.GetIntAttrDatN(nid, "state") == 2):
            tempR += 1
    numberR = tempR
    print "Echo %4d\tnumberR = %5d" % (numberEcho, numberR)
    numberEcho+=1

NIdColorH = snap.TIntStrH()
for NI in net.Nodes():
    nid = NI.GetId()
    if net.GetIntAttrDatN(nid, "state") == 0:
        NIdColorH[nid] = "green"
    elif net.GetIntAttrDatN(nid, "state") == 2:
        NIdColorH[nid] = "red"
    else:
        print "Error! There is infectious node in the network!"

# snap.DrawGViz(snap.GetRndESubGraph(net, 100), snap.gvlDot, "SIRnetwork.png", "SIR Network", False, NIdColorH)


V = snap.TIntV()
sub_node = []
for i in initial_list:
    for connectedNode in net.GetNI(i).GetOutEdges():
        sub_node = list(set(sub_node) | set([connectedNode])) 
    sub_node = list(set(sub_node) | set([i])) 
for nid in sub_node:
    V.Add(nid)
sub = snap.ConvertSubGraph(snap.PNEANet, net, V)

snap.SaveGViz(sub, "SIRsub.dot", "SIR simulation subnet", True, NIdColorH)
snap.SaveGViz(net, "SIRnet.dot", "SIR simulation network", True, NIdColorH)
# output = open("SIR.csv", "w")
# for edge in sub.Edges():
#     output.write( "%d, %d" % (edge.GetSrcNId(),edge.GetDstNId()))
#snap.DrawGViz(sub, snap.gvlDot, "SIRSub.png", "SIR subnetwork", True, NIdColorH)
# test = snap.GetRndSubGraph(sub, 100)
#snap.DrawGViz(test, snap.gvlDot, "SIRSub500.png", "random subgraph 500 nodes, 9204 edges", True, NIdColorH)
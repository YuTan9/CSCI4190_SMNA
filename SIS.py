# CSCI4190 Course project
# Name: Yu-Tang, Shen
# SID: 1155070292
#
# Data: http://snap.stanford.edu/data/soc-Epinions1.html
# Nodes	75879
# Edges	508837
# Nodes in largest WCC	75877 (1.000)
# Edges in largest WCC	508836 (1.000)
# Nodes in largest SCC	32223 (0.425)
# Edges in largest SCC	443506 (0.872)
# Average clustering coefficient	0.1378
# Number of triangles	1624481
# Fraction of closed triangles	0.0229
# Diameter (longest shortest path)	14
# 90-percentile effective diameter	5
import snap
import random 
import sys
import matplotlib.pyplot as plt

#parameters
filename = "soc-Epinions1.txt"
graph = snap.LoadEdgeList(snap.PNGraph, filename, 0, 1)
net = snap.LoadEdgeList(snap.PNEANet, filename, 0, 1)
# contagion_probability = 0.1
# tl = 4 # max step of infection
# contagion_probability = float(sys.argv[1])
# contagion_probability=[]
contagion_probability_base = int(sys.argv[1]) # no less than 1801
tl = int(sys.argv[2]) 
MAX_ECHO = int(sys.argv[3])
initial_list = [18, 737, 118, 40, 27, 19, 0, 4, 5, 10, 12, 28, 34, 77, 136 , 1719] #nodes with high page rank
contagion_probability = snap.TIntFltH()
print "Start simulating SIS model with:"
#print "contagion probability: %f" % contagion_probability
print "contagion probability base: %d" % contagion_probability_base
print "max step of infection: %d" % tl
print "max echo: %d\n\n" %MAX_ECHO
# Simulate SIS model
# state: 
#   0: susceptible
#   1: infectious

#init
print "calculating contagion probability...\n\n"
for NI in net.Nodes():
    nid = NI.GetId()
    state = 0
    if nid in initial_list: 
        state = 1
    else:
        state = 0
    result = net.AddIntAttrDatN(nid, state, "state")
    result = net.AddIntAttrDatN(nid, 0, "step")

    prob = float(NI.GetOutDeg()) / float(contagion_probability_base)
    contagion_probability[nid] = prob
    

#infect
numberEcho = 0
numberSusceptible = net.GetNodes() - len(initial_list)
numberInfectious = len(initial_list)
susceptible = []
infectious = []
echo = []
while numberEcho < MAX_ECHO:
    for NI in net.Nodes():
        nid = NI.GetId()
        if net.GetIntAttrDatN(nid, "state") == 1:
            for connectedNode in NI.GetOutEdges():
                probability = contagion_probability[nid]
                #print "node: %d %d\tall: %d\tnbr: %d\tprob: %f" % (nid, connectedNode,all_nodes, nbr_nodes, contagion_probability)
                if (random.random() < probability) and (net.GetIntAttrDatN(connectedNode, "state") == 0): 
                    result = net.AddIntAttrDatN(connectedNode, 1, "state")
                    numberInfectious += 1
                    numberSusceptible -= 1
            
            nowStep = net.GetIntAttrDatN(nid, "step") + 1
            result = net.AddIntAttrDatN(nid, nowStep, "step")
            if nowStep == tl:
                result = net.AddIntAttrDatN(nid, 0, "state")
                numberSusceptible += 1
                numberInfectious -= 1
    
    print "Echo %4d\tnumberSusceptible = %5d\tnumberInfectious = %5d" % (numberEcho+1, numberSusceptible, numberInfectious)
    susceptible.append(numberSusceptible)
    infectious.append(numberInfectious)
    numberEcho+=1
    echo.append(numberEcho)

NIdColorH = snap.TIntStrH()
for NI in net.Nodes():
    nid = NI.GetId()
    if net.GetIntAttrDatN(nid, "state") == 0:
        NIdColorH[nid] = "green"
    elif net.GetIntAttrDatN(nid, "state") == 1:
        NIdColorH[nid] = "red"
    else:
        print "Error! There is infectious node in the network!"
# F = open("SIS.txt","w") 
# for color in NIdColorH:
#     F.write("%d: %s" % (color, NIdColorH[color]))


# echo = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
plt.plot(echo, susceptible, color='g')
plt.plot(echo, infectious, color='r')
plt.xlabel('Echos')
plt.ylabel('Nodes')
plt.title('SIS simulation over %d echos' % MAX_ECHO)
plt.savefig("SIS_%dtl_%dpb_%decho.png" % (tl, contagion_probability_base, MAX_ECHO))
# plt.savefig("SISTime%dtl%fcp.png" % (tl, contagion_probability))
# plt.show()

#snap.DrawGViz(net, snap.gvlCirco, "SISnetwork.png", "SIS Network", False, NIdColorH)
V = snap.TIntV()
sub_node = []
for i in initial_list:
    for connectedNode in net.GetNI(i).GetOutEdges():
        sub_node = list(set(sub_node) | set([connectedNode])) 
    sub_node = list(set(sub_node) | set([i])) 
for nid in sub_node:
    V.Add(nid)
sub = snap.ConvertSubGraph(snap.PNEANet, net, V)

snap.SaveGViz(sub, "SISsub.dot", "SIR simulation subnet", True, NIdColorH)
snap.SaveGViz(net, "SISnet.dot", "SIR simulation network", True, NIdColorH)
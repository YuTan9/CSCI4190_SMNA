

import snap
import random 
import sys
import matplotlib.pyplot as plt


#############
#PRINT USAGE#
#############
if len(sys.argv) != 5:
    print "Usage: python %s <contagion_probability_base> <max_step_of_infection> <max_echo> <max_step_of_immunity>" % sys.argv[0]
    print "\tcontagion_probability_base: Control the likelihood of spreading infection. The smaller the more likely, with minimum of 1801."
    print "\tmax step of infection: How many echo can a node be infectious."
    print "\tmax echo: How many echo to perform simulation."
    print "\tmax step of immunity: How many echo can a node immune."
    exit(0)



filename = "soc-Epinions1.txt"
graph = snap.LoadEdgeList(snap.PNGraph, filename, 0, 1)
net = snap.LoadEdgeList(snap.PNEANet, filename, 0, 1)

# Simulate SIR model
# state: 
#   0: susceptible
#   1: infectious
#   2: immunity

initial_list = [18, 737, 118, 40, 27, 19, 0, 4, 5, 10, 12, 28, 34, 77, 136 , 1719] #nodes with high page rank
contagion_probability = snap.TIntFltH()
contagion_probability_base = int(sys.argv[1]) # no less than 1801
tl = int(sys.argv[2]) 
MAX_ECHO = int(sys.argv[3])
immunity = int(sys.argv[4])
print "Start simulating SIS model with:"
#print "contagion probability: %f" % contagion_probability
print "contagion probability base: %d" % contagion_probability_base
print "max step of infection: %d" % tl
print "max step of immunity: %d" % immunity
print "max echo: %d\n\n" % MAX_ECHO


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
    result = net.AddIntAttrDatN(nid, 0, "stepImmune")

    prob = float(NI.GetOutDeg()) / float(contagion_probability_base)
    contagion_probability[nid] = prob

#infect
numberEcho = 0
numberSusceptible = net.GetNodes() - len(initial_list)
numberInfectious = len(initial_list)
numberImmune = 0
susceptible = []
infectious = []
immune = []
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
                result = net.AddIntAttrDatN(nid, 2, "state")
                numberInfectious -= 1
                numberImmune += 1
        if net.GetIntAttrDatN(nid, "state") == 2:
            nowStepImmune = net.GetIntAttrDatN(nid, "stepImmune") + 1
            result = net.AddIntAttrDatN(nid, nowStep, "stepImmune")
            if nowStepImmune == immunity:
                result = net.AddIntAttrDatN(nid, 0, "state")
                numberSusceptible += 1
                numberImmune -= 1
    susceptible.append(numberSusceptible)
    infectious.append(numberInfectious)
    immune.append(numberImmune)
    numberEcho+=1
    echo.append(numberEcho)
    print "Echo %4d\tnumberSusceptible = %5d\tnumberInfectious = %5d\tnumberImmune = %5d" % (numberEcho, numberSusceptible, numberInfectious, numberImmune)



plt.plot(echo, susceptible, color='g')
plt.plot(echo, infectious, color='r')
plt.plot(echo, immune, color='b')
plt.xlabel('Echos')
plt.ylabel('Nodes')
plt.title('SIRS simulation over %d echos' % MAX_ECHO)
plt.savefig("SIRS_%dtl_%dpb_%decho.png" % (tl, contagion_probability_base, MAX_ECHO))

def colorNet(net):
    NIdColorH = snap.TIntStrH()
    for NI in net.Nodes():
        nid = NI.GetId()
        if net.GetIntAttrDatN(nid, "state") == 0:
            NIdColorH[nid] = "green"
        elif net.GetIntAttrDatN(nid, "state") == 2:
            NIdColorH[nid] = "red"
        else:
            print "Error! There is infectious node in the network!"
    return net

V = snap.TIntV()
sub_node = []
for i in initial_list:
    for connectedNode in net.GetNI(i).GetOutEdges():
        sub_node = list(set(sub_node) | set([connectedNode])) 
    sub_node = list(set(sub_node) | set([i])) 
for nid in sub_node:
    V.Add(nid)
sub = snap.ConvertSubGraph(snap.PNEANet, net, V)

snap.SaveGViz(sub, "SIRSsub.dot", "SIR simulation subnet", True, NIdColorH)
snap.SaveGViz(net, "SIRSnet.dot", "SIR simulation network", True, NIdColorH)
    
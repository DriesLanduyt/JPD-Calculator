# -*- coding: utf-8 -*-
"""
@author: LANDUYTD

Requirements for nets developed with the Netica GUI:
    * Nets have to have a nodeset 'IN' for the inputnodes and a nodeset 'OUT' for the output nodes
    * For the inputnodes, statenames are used and have to be defined
    * For the outputnodes, statetitles are used and have to be defined numerically
    * Netica.dll has to be in the working directory
"""
import itertools
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm


def allJPDs(net):
    """
    Automatically generates JPDs for all pairs of nodes assigned to the nodeset
    'OUT' (see Netica GUI user's guide for more info on nodesets)
    """
    
    onodes = net.Outputnodes()
    combinations = [i for i in itertools.combinations(onodes,2)]
    JPDdata = []    
    for c in combinations:
        priorA = getPrior(net,c[0])
        priorB = getPrior(net,c[1]) 
        jpd = JPD(net,c)
        cov = Covariance (priorA,priorB,jpd)
        cor = Correlation (priorA,priorB,cov) 
        JPDdata.append([c[0],c[1],jpd,cov,cor])
    return JPDdata
    
def JPD(net,nodeTuple):
    """
    Generates a joint probability distribution for a specified pair of nodes. 
    Returns a matrix with bottom left the first states (low values) of the 
    statelists and top right the last states (high values) of the statelists
    """   

    priorA = getPrior(net,nodeTuple[0])   
    statesA = net.NodeStates(nodeTuple[0],naming = 'titlename') 
    statesB = net.NodeStates(nodeTuple[1],naming = 'titlename')
    numstatesA = [float(i) for i in statesA] 
    numstatesB = [float(i) for i in statesB]    
    output = np.zeros((len(statesA)+1,len(statesB)+1))
    output[0,1:] = numstatesB
    output[1:,0] = numstatesA
    for n,i in enumerate(statesA):
        net.RetractFinding()       
        output[n+1][1:] = np.array(net.Finding(nodeTuple[0],i,nodeTuple[1],output = 'name'))*priorA[0][n]
    return output
    
def allcJPDs(net,cond_node,cond_states):
    """
    Automatically generates conditional JPDs for all pairs of nodes assigned to
    the nodeset 'OUT' (see Netica GUI user's guide for more info on nodesets). 
    All JPDs all calculated conditional on "cond_node" being in a specific 
    state. The code loops through the list of states (of "cond_node") provided 
    by the user.
    """
    
    onodes = net.Outputnodes()
    onodes = sorted(onodes)
    combinations = [i for i in itertools.combinations(onodes,2)]
    JPDdatas = []    
    progress = 0
    for cs in cond_states:
        JPDdata = []
        for c in combinations:
            print 'Progress: ' +str(int(100*float(progress)/float(len(combinations)*len(cond_states))))+ ' %'
            priorA = getCondPrior(net,c[0],cond_node,cs)
            print priorA
            priorB = getCondPrior(net,c[1],cond_node,cs) 
            print priorB
            JPD = cJPD(net,c,cond_node,cs)
            cov = Covariance (priorA,priorB,JPD)
            cor = Correlation (priorA,priorB,cov) 
            JPDdata.append([c[0],c[1],JPD,cov,cor])
            progress+=1
        JPDdatas.append(JPDdata)
    return JPDdatas

def cJPD(net,nodeTuple,cond_node,cond_state):
    """
    Generates a joint probability distribution for a specified pair of nodes, 
    conditional on "cond_node being in state "cond_state". Returns a matrix 
    with bottom left the first states (low values) of the statelists and top 
    right the last states (high values) of the statelists
    """
    
    priorA = getCondPrior(net,nodeTuple[0],cond_node,cond_state)
    statesA = net.NodeStates(nodeTuple[0],naming = 'titlename') 
    statesB = net.NodeStates(nodeTuple[1],naming = 'titlename')
    numstatesA = [float(i) for i in statesA] 
    numstatesB = [float(i) for i in statesB]    
    output = np.zeros((len(statesA)+1,len(statesB)+1))
    output[0,1:] = numstatesB
    output[1:,0] = numstatesA
    for n,i in enumerate(statesA):
        if priorA[0][n]== 0: 
            output[n+1][1:] = np.array([0.0]*len(statesB))
            print 'zero belief vector'
        else: 
            output[n+1][1:] = np.array(net.Findings([cond_node,nodeTuple[0]],[cond_state,n],nodeTuple[1],output = 'name',ranks = [False,True]))*priorA[0][n]
    return output
   
   
# Draw functions
#---------------

def drawAllJPDs(data):
    fs = 12
    outputnodes =[] 
    for d in data:
        if d[0] not in outputnodes: outputnodes.append(d[0])
        if d[1] not in outputnodes: outputnodes.append(d[1])
    size = len(outputnodes) 
    #fill multipanel plot
    for i in range(size):
        for j in range(size):
            plt.subplot(size,size,i*size+j+1)
            if i==j:
                plt.text(0.5,0.5,outputnodes[i],fontsize=fs,horizontalalignment='center',verticalalignment='center')
            else:
                nodes = [outputnodes[i],outputnodes[j]]
                if j<i:
                    for d in data:
                        if set(d[0:2])==set(nodes):
                            cor = d[4]
                            plt.text(0.5,0.5,"%.2g" %cor,fontsize=fs,horizontalalignment='center',verticalalignment='center') #style van cor nog aanpassen
                else:
                    for d in data:
                        if d[0:2]==nodes:
                            jpd = np.array(d[2])[1:,1:]
                            imgplot = plt.imshow(np.absolute(jpd[::-1]),cmap = cm.binary,vmin = 0, vmax = 0.2) #norm = matplotlib.colors.LogNorm() #omdraaien zodat eerste states uit statelists (laagste waarden) onderaan links staan
                            imgplot.set_interpolation('nearest')
            plt.xticks((),())
            plt.yticks((),())

def drawJPD(data):
    jpd = np.array(data)[1:,1:]
    imgplot = plt.imshow(np.absolute(jpd[::-1]),cmap = cm.binary,vmin = 0, vmax = 0.2)
    imgplot.set_interpolation('nearest')

# Helper functions
#-----------------
    
def getPrior(net,node):
    net.RetractFinding()
    states = [float(i) for i in net.NodeStates(node,naming = 'titlename')]
    belief = net.Likelihood(node)
    mn = sum([float(states[j])*belief[j] for j in range(len(belief))])
    std = np.sqrt(sum([((float(states[j])-mn)**2)*belief[j] for j in range(len(belief))]))
    return [belief,mn,std]
    
def getCondPrior(net,node,cond_node,cond_state):
    net.RetractFinding()
    states = [float(i) for i in net.NodeStates(node,naming = 'titlename')]
    belief = net.Finding(cond_node,cond_state,node,output = 'name',rank = False)
    mn = sum([float(states[j])*belief[j] for j in range(len(belief))])
    std = np.sqrt(sum([((float(states[j])-mn)**2)*belief[j] for j in range(len(belief))]))
    return [belief,mn,std] 
    
def Correlation(priorA,priorB,cov):
    return  cov/(priorA[2]*priorB[2])  
    
def Covariance(priorA,priorB,JPD):
    cov = 0 
    JPD = np.array(JPD)
    for r,row in enumerate(JPD[1:,1:]):
        for n,el in enumerate(row): 
            cov+=el*(JPD[0,1:][n]-priorB[1])*(JPD[1:,0][r]-priorA[1])
    return cov



        



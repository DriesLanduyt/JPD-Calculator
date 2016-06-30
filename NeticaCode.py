# -*- coding: utf-8 -*-
"""
@author: LANDUYTD

Requirements for nets developed with the Netica GUI:
    * Nets have to have a nodeset 'IN' for the inputnodes and a nodeset 'OUT' for the output nodes
    * For the inputnodes, statenames are used and have to be defined
    * For the outputnodes, statetitles are used and have to be defined numerically
    * Netica.dll has to be in the working directory
"""

import os
import ctypes as ct
import numpy as np

class OpenBayesNet():
    
    def __init__ (self, netname, password=None):
        """
        Initialize network object. The Licensefile for the Netica.dll, if present, can be provided in the code below
        """
        
        #create new environment 
        if '/' in netname:
            directarray = netname.split('/')           
            direct  = '/'.join(directarray[0:-1])
            netname = directarray[-1]
        else: 
            direct = os.getcwd()

        self.n = ct.windll.Netica                 
        self.env = ct.c_void_p(self.n.NewNeticaEnviron_ns(password,None,None))
        self.mesg = ct.create_string_buffer('\000' * 1024)
        self.n.InitNetica2_bn(self.env, ct.byref(self.mesg))

        os.chdir(direct)
        
        #Open net from provided file
        streamer = self.n.NewFileStream_ns(netname,self.env,None)
        cnet = self.n.ReadNet_bn(streamer,0x10) #0x10 is a constant taken from Netica.h
        self.net = cnet
        
        #Disable automatic updating
        self.n.SetNetAutoUpdate_bn(self.net, 0) 
        
        #Identify input, output and intermediate nodes
        inputnodeset = ct.c_char_p('IN')
        outputnodeset = ct.c_char_p('OUT')
        outputcnodes = []
        inputcnodes = []
        all_nodes = self.n.GetNetNodes2_bn (self.net,None)
        internodes = 0
        for t in range(self.n.LengthNodeList_bn(all_nodes)):            
            cn = self.n.NthNode_bn(all_nodes,t)            
            if self.n.IsNodeInNodeset_bn(self.n.NthNode_bn(all_nodes,t),inputnodeset): inputcnodes.append(cn)
            elif self.n.IsNodeInNodeset_bn(self.n.NthNode_bn(all_nodes,t),outputnodeset): outputcnodes.append(cn)
            else: internodes+=1
        self.output, self.input= outputcnodes,inputcnodes
        self.numberofnodes = [len(inputcnodes),internodes,len(outputcnodes)]

        #Compile network
        self.n.CompileNet_bn(cnet)
     
     
    def __repr__(self):
        """
        Representation of a network object in the python command line
        """
        
        name = ct.cast(self.n.GetNetName_bn(self.net),ct.c_char_p).value
        numnodes = str(self.numberofnodes)
        
        inputnodes,outputnodes = [],[]
        for i in self.input:
            inputnodes.append(ct.cast(self.n.GetNodeName_bn(i),ct.c_char_p).value)
        inodes = ','.join(inputnodes)
        for j in self.output:
            outputnodes.append(ct.cast(self.n.GetNodeName_bn(j),ct.c_char_p).value)
        onodes = ','.join(outputnodes)
        
        return ' netname: '+ name +'\n number of nodes (i,int,o): '+ numnodes + '\n inputnodes: ' + inodes +'\n outputnodes: ' + onodes
        
    def Netname(self):
        """
        Returns the name of the network model
        """
        
        return ct.cast(self.n.GetNetName_bn(self.net),ct.c_char_p).value
                
    def Outputnodes(self):
        """
        returns an array of the names of the outputnodes
        """
        
        return [ct.cast(self.n.GetNodeName_bn(j),ct.c_char_p).value for j in self.output]
        
    def Inputnodes(self):
        """
        returns an array of the names of the inputnodes
        """
        
        return [ct.cast(self.n.GetNodeName_bn(j),ct.c_char_p).value for j in self.input]
        
    
    def NodeStates(self,node,naming='statename'):
        """        
        returns the states of a node        
        """
        
        cnode = self.n.GetNodeNamed_bn(node,self.net)
        y = self.n.GetNodeNumberStates_bn(cnode)
        states = []
        for j in range(y):
            if naming == 'statename': states.append(ct.cast(self.n.GetNodeStateName_bn(cnode,j),ct.c_char_p).value)
            elif naming == 'titlename': states.append(ct.cast(self.n.GetNodeStateTitle_bn(cnode,j),ct.c_char_p).value)
        return states

    def Finding(self,node,state,outputnode,output = 'nr',rank = False):
        ''' 
        Enter finding 'state' in particular node 'node' and retrieve beliefs of the 'outputnodenr'th outputnode 
        '''   
        
        self.RetractFinding()
        cnode = self.n.GetNodeNamed_bn(node,self.net)
        if output == 'nr': ocnode = self.n.GetNodeNamed_bn(self.Outputnodes()[outputnode-1],self.net)
        elif output == 'name': ocnode = self.n.GetNodeNamed_bn(outputnode,self.net)       
        x = self.n.GetNodeNumberStates_bn(ocnode) 
        if rank ==False: cstate = self.n.GetStateNamed_bn(state,cnode)
        else: cstate = state 
        self.n.EnterFinding_bn(cnode,cstate)
        return ct.cast(self.n.GetNodeBeliefs_bn(ocnode),ct.POINTER(ct.c_float))[0:x]
        
    def Findings(self,nodes,states,outputnode,ranks,output = 'nr'):
        ''' 
        Enter finding 'state' in particular node 'node' and retrieve beliefs of the 'outputnodenr'th outputnode 
        '''   
        
        self.RetractFinding()
        for i,node in enumerate(nodes):
            cnode = self.n.GetNodeNamed_bn(node,self.net) 
            if ranks[i] ==False: cstate = self.n.GetStateNamed_bn(states[i],cnode)
            else: cstate = states[i] 
            self.n.EnterFinding_bn(cnode,cstate)
        if output == 'nr': ocnode = self.n.GetNodeNamed_bn(self.Outputnodes()[outputnode-1],self.net)
        elif output == 'name': ocnode = self.n.GetNodeNamed_bn(outputnode,self.net)       
        x = self.n.GetNodeNumberStates_bn(ocnode)
        return ct.cast(self.n.GetNodeBeliefs_bn(ocnode),ct.POINTER(ct.c_float))[0:x] 

    def Likelihood(self,node):
        """
        Extracts a probability distribution for a specific node
        """
        
        cnode = self.n.GetNodeNamed_bn(node,self.net)
        x = self.n.GetNodeNumberStates_bn(cnode) 
        return ct.cast(self.n.GetNodeBeliefs_bn(cnode),ct.POINTER(ct.c_float))[0:x]

    def RetractFinding(self):
        """
        Retracts all finding from a network
        """
        
        self.n.RetractNetFindings_bn(self.net)
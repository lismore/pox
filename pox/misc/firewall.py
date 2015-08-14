''' Firewall Class for PoX SDN Controller '''

from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.revent import *
from pox.lib.util import dpidToStr
from pox.lib.addresses import EthAddr
from collections import namedtuple
import os

mylogger = core.getLogger()
policies = "%s/pox/pox/misc/firewall-policies.csv" % os.environ[ 'HOME' ]  

class Firewall (EventMixin):

    def __init__ (self):
        self.listenTo(core.openflow)
        mylogger.debug("Starting Firewall Module")
	print "Firewall instance registered"

    def _handle_ConnectionUp (self, event):    
        with open(policies) as policyfile:
            for eachlines in policyfile:
                id, mac1, mac2 = eachlines.split(',')
                if id != 'id':
                    for i in range(2):
                        flowmod = of.ofp_flow_mod(#action = of.ofp_action_output(port = of.OFPP_NONE),  
                                                priority = 1000)
                        if i == 0:
                            flowmod.match.dl_src = EthAddr(mac1)
                            flowmod.match.dl_dst = EthAddr(mac2)
                        else:
                            flowmod.match.dl_src = EthAddr(mac2)
                            flowmod.match.dl_dst = EthAddr(mac1)
                        event.connection.send(flowmod)
        mylogger.debug("Firewall rules installed on %s", dpidToStr(event.dpid))
     
    def test():
   	print "Firewall instance registered"
    
    def AddRule(rule):
	
	'''TODO Add Firewall Rule Logic'''

    def DeleteRule(rule):

	'''TODO Delete Firewall Rule Logic'''

    def GetRules():
       with open(policies) as policyfile:
	for eachline in policyfile:
	 id, mac1, mac2, = eachline.split(',')
	 print "Rule: ID= " +  id + "Mac 1 =" + mac1 + "Mac 2= " +  mac2

def launch ():
    '''
    Firewall module Started
    '''
    core.registerNew(Firewall)


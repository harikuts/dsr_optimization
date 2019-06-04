#!/usr/bin/env python
# -*- coding: utf-8 -*-


# For bug reports, feature and support requests please visit
# <https://github.com/mkalewski/sim2net/issues>.

"""
sim2net -- simulation application file.

If in any doubt, refer to the technical documentations that is available on the
Internet:  <https://sim2net.readthedocs.org/en/latest/>.
"""

import pdb
import random

MSG_TYPE = 0
RREQ_TYPE = 1
RREP_TYPE = 2
RERR_TYPE = 3

RREQ_WAIT_TIME = 25
STATIC_TIMEOUT = 5000
MSG_LIFE = 10000
NODE_MEM_SPAN = 25

PKT_DIV = "|"

from sim2net.application import Application

class dsr_msg:
    # GENERAL PACKET FORMAT
    # packet (ALL, optional)
    # mtype (ALL)
    # src_id (ALL)
    # dest_id (ALL)
    # target_id (MSG_TYPE, RREP_TYPE, RERR_TYPE)
    # message (MSG_TYPE)
    # path (ALL)
    
    def __init__(self, packet=None, mlife=None, mtype=None, \
        src_id=None, dest_id=None, target_id=None, \
            message=None, path=None, new_msg=False):
        if packet:
            self.extract_packet(packet)
        else:
            self.mlife = mlife
            self.mtype = mtype
            self.src = src_id
            self.dest = dest_id
            self.target = target_id
            self.message = message
            self.path = path
        if new_msg:
            self.mlife = MSG_LIFE
        self._zip_packet()
            
    def extract_packet(self, pkt):
        contents = pkt.split(PKT_DIV)
        self.mlife = None if contents[0] == str(None) else int(contents[0])
        self.mtype = None if contents[1] == str(None) else int(contents[1])
        self.src = None if contents[2] == str(None) else int(contents[2])
        self.dest = None if contents[3] == str(None) else int(contents[3])
        self.target = None if contents[4] == str(None) else int(contents[4])
        self.message = None if contents[5] == str(None) else str(contents[5])
        try:
            self.path = [int(node) for node in contents[6:]]
        except IndexError:
            self.path = []

    def _zip_packet(self):
        params = []
        params += [self.mlife, self.mtype, self.src, self.dest, self.target, self.message]
        params += self.path
        params = [str(param) for param in params]
        self.packet = PKT_DIV.join(params)
    

class HelloWorld(Application):
    """
    A "Hello World" example with two nodes: the node with ID equal 0 sends a
    message that should be received and printed by the node with ID equal to 1.
    (See also the ``configuration.py`` file.)

    For more information about the methods that follows refer to the technical
    documentation:
    """

    def initialize(self, node_id, shared):
        """
        Initialization method.
        """
        self.__node_id = node_id
        self.route_table = {}
        self.route_lifetimes = {}
        self.neighbors = []
        self.communication = None
        self.buff = [None] * 8
        self.last_rrep_dest = None
        self.last_rrep_time = None
        self.last_rreq_dest = None
        self.last_rreq_time = None
        print '[node %d] initialize' % self.__node_id

    def finalize(self, shared):
        """
        Finalization method.
        """
        print '[node %d] finalize' % self.__node_id

    def failure(self, time, shared):
        """
        This method is called only if the node crashes.
        """
        print ('[node %d] failure @ (%d, %2f)'
               % (self.__node_id, time[0], time[1]))

    def main(self, time, communication, neighbors, shared):
        """
        This method is called at each simulation step.
        """
        
        # Update neighbors
        self.neighbors = neighbors
        self.communication = communication
        
        #Route table maintenace
        #for entry in self.route_table.keys():
            #self.route_lifetimes[entry] -= 1
            #if self.route_lifetimes[entry] <= 0:
                #print("Route for %d has expired." % (entry))
                #del self.route_table[entry]
                #del self.route_lifetimes[entry]
        
        # Last RREQ/RREP memory maintenance
        if self.last_rreq_time > 0:
            self.last_rreq_time -= 1
        else:
            self.last_rreq_dest = None
        if self.last_rrep_time > 0:
            self.last_rrep_time -= 1
        else:
            self.last_rrep_dest = None
        
        
        #print("main for", self.__node_id)
        if self.__node_id == 0:
        #if self.__node_id == 0:
            #print("S: %d->ALL" % self.__node_id)
            #communication.send('hi')
            # Repeatedly send hi messages out
            if None not in self.route_table.values():
                buff_occupied = False
                for i in range(len(self.buff)):
                    if self.buff[i] is not None:
                        buff_occupied = True
                        self.dispatch_msg(self.__node_id, i, self.buff[i])
                        break
                        print ("Sending from buffer '%s' to %d" % (self.buff[i], i))
                        self.buff[i] = None
                if not buff_occupied:
                    target = random.randint(1,7)
                    message = "hi"
                    print ("Sending '%s' to %d" % (message, target))
                    self.dispatch_msg(self.__node_id, target, message)
        while True:
            #print ("%d's neighbors:" % self.__node_id, neighbors)
            msg = communication.receive()
            if msg is None:
                break
            #print ('===== R: %d<-%d ====='
                   #% (self.__node_id, msg[0]))
            self.handle_msg(msg[0], msg[1])
            
            
    def dispatch_msg(self, src_id, dest_id, message):
        # If cached route is available
        if dest_id in self.route_table.keys() and self.route_table[dest_id] is not None:
            # Then send it along that path
            print("\tomw")
            pass
        # If we need to find a route
        else:
            self.buff[dest_id] = message
            print ("Need path from %d to %d" % (src_id, dest_id))
            self.route_table[dest_id] = None
            self.route_lifetimes[dest_id] = RREQ_WAIT_TIME
            # Send a new RREQ
            self.forward_rreq(src_id, self.__node_id, dest_id, path=[], new_msg=True)
        pass
    
    def forward_msg(self, src_id, cur_id, dest_id, content):
        pass
    
    def forward_rreq(self, src_id, cur_id, dest_id, path, msg_life=0, new_msg=False):
        if cur_id not in path and dest_id != self.last_rreq_dest:
            self.last_rreq_dest = dest_id
            self.last_rreq_time = NODE_MEM_SPAN
            path.append(cur_id)
            rreq = dsr_msg(mlife=msg_life, mtype=RREQ_TYPE, src_id=src_id, dest_id=dest_id, path=path, new_msg=new_msg)
            self.communication.send(rreq.packet)
    
    def forward_rrep(self, src_id, target_id, dest_id, path, msg_life=0, new_msg=False):
        if dest_id != self.last_rrep_dest:
            self.last_rrep_dest = dest_id
            self.last_rrep_time = NODE_MEM_SPAN
            rrep = dsr_msg(mlife=msg_life, mtype=RREP_TYPE, src_id=src_id, target_id=target_id, dest_id=dest_id, path=path)
            self.communication.send(rrep.packet)
    
    def handle_msg(self, from_here, packet):
        msg = dsr_msg(packet=packet)
        msg.mlife -= 1
        
        # Handle RREQ messages
        if msg.mtype == RREQ_TYPE:
            #print("%d got a RREQ from %d with path %s." % (self.__node_id, from_here, str(msg.path)))
            if msg.dest == self.__node_id:
                print("Reached %d. Sending back to %d." % (msg.dest, msg.path[-1]))
                # Send a new reply back
                self.forward_rrep(msg.src, msg.path[-1], msg.dest, msg.path+[self.__node_id], new_msg=True)
                pass
            else:
                self.forward_rreq(msg.src, self.__node_id, msg.dest, msg.path, msg_life=msg.mlife)
        
        # Handle RREP messages
        if msg.mtype == RREP_TYPE and 1 > 0 and msg.target == self.__node_id:
            print("%d got a RREP from %d with path %s." % (self.__node_id, from_here, str(msg.path)))
            # If RREP has been received at the source, then add it to the routing table
            if msg.src == self.__node_id:
                print("\tRREP has reached the source.")
                #pdb.set_trace()
                if msg.dest in self.route_table.keys():
                    if self.route_table[msg.dest] is None:
                        print ("\n[Adding] path from [%d] to [%d]: %s\n" % (msg.src, msg.dest, str(msg.path)))
                        self.route_table[msg.dest] = msg.path
                        self.route_lifetimes[msg.dest] = STATIC_TIMEOUT
            else:
                target = msg.path[msg.path.index(self.__node_id) - 1]
                #print("\tForward targeted at %d." % (target))
                self.forward_rrep(msg.src, target, msg.dest, msg.path, msg_life=msg.mlife)
            

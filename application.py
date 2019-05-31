#!/usr/bin/env python
# -*- coding: utf-8 -*-


# For bug reports, feature and support requests please visit
# <https://github.com/mkalewski/sim2net/issues>.

"""
sim2net -- simulation application file.

If in any doubt, refer to the technical documentations that is available on the
Internet:  <https://sim2net.readthedocs.org/en/latest/>.
"""

MSG_TYPE = 0
RREQ_TYPE = 1
RREP_TYPE = 2
RERR_TYPE = 3

PKT_DIV = "|"

from sim2net.application import Application

class dsr_msg:
    def __init__(self, packet=None, src_id=None, dest_id=None, content=None, count=None):
        if packet:
            self.extract_packet(packet)
        else:
            self.mtype = MSG_TYPE
            self.src = src_id
            self.dest = dest
            # Standard message, RERR
            if self.mtype == MSG_TYPE or self.mtype == RERR_TYPE:
                self.message = content
                self.count = count
            # RREQ, RREP
            if self.mtype == RREQ_TYPE or self.mtype == RREP_TYPE:
                self.path = path
            
    def extract_packet(self, pkt):
        contents = pkt.split(PKT_DIV)
        self.mtype = int(contents[0])
        self.src = int(contents[1])
        self.dest = int(contents[2])
        # Standard message, RERR
        if self.mtype == MSG_TYPE or self.mtype == RERR_TYPE:
            self.message = int(contents[3])
        # RREQ, RREP
        if self.mtype == RREQ_TYPE or self.mtype == RREP_TYPE:
            try:
                self.path = [int(node) for node in contents[3:]]
            except IndexError:
                self.path = []
    def _zip_packet(self):
        if self.mtype == MSG_TYPE or self.mtype == RERR_TYPE:
            self.packet = PKT_DIV.join([str(self.mtype), str(self.src), str(self.dest), self.message])
        if self.mtype == RREQ_TYPE or self.mtype == RREP_TYPE:
            self.packet = PKT_DIV.join([str(self.mtype), str(self.src), str(self.dest), *self.path])
    

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
        self.routing_table = {}
        self.routing_lifetimes = {}
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
        #print("main for", self.__node_id)
        #if self.__node_id == 0 and time[0] == 1:
        if self.__node_id == 0:
            print("S: %d->ALL" % self.__node_id)
            communication.send('hi')
        while True:
            msg = communication.receive()
            if msg is None:
                break
            print ('R: %d<-%d: "%s"'
                   % (self.__node_id, msg[0], msg[1]))
            
    def dispatch_msg(self, src_id, dest_id, message):
        
    
    def handle_msg(self, 
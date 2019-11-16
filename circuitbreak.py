#!/usr/bin/env python

#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements. See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership. The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License. You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied. See the License for the
# specific language governing permissions and limitations
# under the License.
#
import glob
import sys
import time
import threading

sys.path.append('gen-py')
sys.path.insert(0, glob.glob('../thrift-0.13.0/lib/py/build/lib*')[0])

from tutorial import Calculator
from tutorial.ttypes import InvalidOperation, Operation, Work

from shared.ttypes import SharedStruct

from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer

from thrift import Thrift

class Handler:
    def __init__(self):
        self.log = {}

    def ping(self):
        if state.failure_count == state.failure_threshold: 
            state.circuitOpen()
        try:
            transport.open()
            client.ping()
            print('Ping sucessfully send')
            transport.close()
            state.closed()
        except Thrift.TException as tx:
            print('%s' % tx.message)
            print('Failure to connect to server during ping')
            state.connectionFail()
        transport.close()

    def calculate(self, logid, work):
        if state.failure_count == state.failure_threshold:
            state.circuitOpen()
        try:
            transport.open()
            print('Calculating...')
            val = client.calculate(1, work)
            print('Calcule Successfully Finished')
            transport.close()
            state.failure_count = 0
            return val
        except Thrift.TException as tx:
            print('%s' % tx.message)
            print('Failure to connect to server during calculate')
            state.connectionFail()
        transport.close()
    
class CircuitBreaker:
    def __init__(self,failure_count=0,failure_threshold=2,reset_timeout=5):
        self.failure_count = failure_count
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        
    def closed(self): ## Resets the failure_count, all good here
        self.failure_count = 0
        print('Connection CLIENT-SERVER OK, circuit is currently closed')
    
    def connectionFail(self): ## Increase the failure_count, something is not working properly
        self.failure_count +=1
        print('Failure count = %d' % self.failure_count)
        if self.failure_count == self.failure_threshold:
            print('\n ---> Failure Threshold reached, state moved to Open')
            state.opened()
          
    def opened(self): ## Server is in open state, need to start a secondary thread to handle the requests from client and test connection with server at the same time
        print('Circuit in Opened State')
        state.startThreading()

    def halfOpen(self): ## Tests rather or not connection with Server was reestabilished
        print('\n ---> State moved to Half-Open, testing if connection with Server was reestablished')
        try: 
            transport.open()
            client.ping()
            transport.close()
            print('\nLooks like server is online!')
            state.closed()
        except Thrift.TException as tx:   
            transport.close()  
            print('%s' % tx.message)
            print('\nConnection test during Half-Open FAILED!!! Going back to Open circuit')
            state.opened()
    
    def startThreading(self, success=False): ## Starts a secondary thread to test the CB-Server connection
        t = threading.Thread(target=state.secondaryThread)
        t.daemon = True
        print('\t Initializing primary thread')
        t.start()
    
    def secondaryThread(self): ## Count to 5 then move from open to half-open
        print('\t Initializing secondary thread')
        time.sleep(self.reset_timeout)
        state.halfOpen() 
    
    def circuitOpen(self): ## Handles requets from client while the circuit is open
        open_message = Thrift.TApplicationException()
        open_message.message='Circuit is currently OPEN, try again later'
        raise open_message




if __name__ == '__main__':
    handler = Handler()
    processor = Calculator.Processor(handler)
    server_transport = TSocket.TServerSocket(host='127.0.0.1', port=9090)
    tfactory = TTransport.TBufferedTransportFactory()
    pfactory = TBinaryProtocol.TBinaryProtocolFactory()
    server = TServer.TSimpleServer(processor, server_transport, tfactory, pfactory)

    transport = TSocket.TSocket('localhost', 9000)
    transport.setTimeout(10) ## Time out 
    transport = TTransport.TBufferedTransport(transport)
    protocol = TBinaryProtocol.TBinaryProtocol(transport)
    client = Calculator.Client(protocol)
    
    print('Starting the circuit breaker...')
    state = CircuitBreaker()
    server.serve()
    print('done.')

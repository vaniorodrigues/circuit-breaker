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

class CircuitBreaker:
    def __init__(self):
        self.log = {}

    def ping(self):
        if state.failure_count == state.failure_threshold:
            state.opened()
        if state.failure_count > state.failure_threshold:
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

    def calculate(self, logid, work):
        if state.failure_count == state.failure_threshold:
            state.opened()
        try:
            transport.open()
            print('Calculating...')
            val = client.calculate(1, work)
            print('Calcule Successfully Finished')
            transport.close()
            state.closed()
            return val
        except Thrift.TException as tx:
            print('%s' % tx.message)
            print('Failure to connect to server during calculate')
            state.connectionFail()
 
    
class State:
    def __init__(self,failure_count=0,failure_threshold=2):
        self.failure_count = failure_count
        self.failure_threshold =failure_threshold
        
    def closed(self): ## Reset the count
        self.failure_count = 0
        print('Connection Sucessfull, state is currently closed')
    
    def connectionFail(self): ## Increase the count
        self.failure_count +=1
        print('connectionFail, increasing failure count')
        print('failure count %d' % self.failure_count)
        if self.failure_count == self.failure_threshold:
            print('State changing to Open, sleeping now...')
            state.opened()
          
    def opened(self):
        self.failure_count +=1
        state.update()
        print('Circuit in Opened State')

    def halfOpened(self):
        print('State moved to Half-Opened, waiting for next request')
        ## Testa para se a conexao com o servidor foi reestabelecida
        try: 
            transport.open()
            client.ping()
            transport.close()
            print('Looks like server is online!')
            state.closed()
        except Thrift.TException as tx:   
            transport.close()  
            print('%s' % tx.message)
            print('Open Circuit: Server is OFFLINE!')
            state.opened()
    
    def update(self, success=False):
        t = threading.Thread(target=state.delayed_update)
        t.daemon = True
        print('\t Initializing primary thread')
        t.start()
    
    def delayed_update(self):
        print('\t Initializing secondary thread')
        time.sleep(5)
        state.halfOpened() 
    
    def circuitOpen(self):
        open_message = Thrift.TApplicationException()
        open_message.message='Circuit is currently OPEN, try again later'
        raise open_message

if __name__ == '__main__':
    handler = CircuitBreaker()
    processor = Calculator.Processor(handler)
    server_transport = TSocket.TServerSocket(host='127.0.0.1', port=9090)
    tfactory = TTransport.TBufferedTransportFactory()
    pfactory = TBinaryProtocol.TBinaryProtocolFactory()
    server = TServer.TSimpleServer(processor, server_transport, tfactory, pfactory)

    transport = TSocket.TSocket('localhost', 9000)
    transport.setTimeout(1000) ## Time out 
    transport = TTransport.TBufferedTransport(transport)
    protocol = TBinaryProtocol.TBinaryProtocol(transport)
    client = Calculator.Client(protocol)
    
    print('Starting the circuit breaker...')
    state = State()
    server.serve()
    print('done.')



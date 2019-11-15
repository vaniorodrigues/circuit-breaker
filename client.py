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

import sys
import glob
import time
sys.path.append('gen-py')
sys.path.insert(0, glob.glob('../thrift-0.13.0/lib/py/build/lib*')[0])

from tutorial import Calculator
from tutorial.ttypes import InvalidOperation, Operation, Work

from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol


def main():
    # Make socket
    transport = TSocket.TSocket('localhost', 9090)
    transport.setTimeout(2000)
    # Buffering is critical. Raw sockets are very slow
    transport = TTransport.TBufferedTransport(transport)

    # Wrap in a protocol
    protocol = TBinaryProtocol.TBinaryProtocol(transport)
    # Create a client to use the protocol encoder
    client = Calculator.Client(protocol)

    # Connect!
    transport.open()
    work = Work()
    
    work.op = Operation.DIVIDE
    work.num1 = 1
    work.num2 = 0
    '''
    try:
        quotient = client.calculate(1, work)
        print('Whoa? You know how to divide by zero?')
        print('FYI the answer is %d' % quotient)
    except InvalidOperation as e:
        print('InvalidOperation: %r' % e)

    work.op = Operation.ADD
    work.num1 = 2
    work.num2 = 2
    sum_ = client.calculate(1, work)  
    print('2+2=%d' % sum_)
    
    work.op = Operation.SUBTRACT
    work.num1 = 15
    work.num2 = 10
    diff = client.calculate(1, work)
    print('15-10=%d' % diff)

    #try:
    #client.serverSleep10()
    input()
    
    client.ping()
    print('ping()')
    '''

    
    #except Thrift.TException as e:
    #    print('%s' % e.message)
    #    print('Deu ruim')
    

    #work.op = Operation.ADD
    #work.num1 = 15
    #work.num2 = 10
    #diff = client.calculate(1, work)
    #print('15-10=%d' % diff)

    #log = client.getStruct(1)
    #print('Check log: %s' % log.value)

    # Close!
    transport.close()


if __name__ == '__main__':
    try:
        main()
    except Thrift.TException as tx:
        print('%s' % tx.message)

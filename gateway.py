#!/usr/bin/python

#Copyright (c) 2009 Gonzalo Sainz-Trapaga
#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in
#all copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#THE SOFTWARE.

import bluetooth
import select
import pdu

DEBUG = False

class Nokia6103:
    def __init__(self, hwaddr, port):
        self.sockfd = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        self.sockfd.connect((hwaddr, port))
        self._send('ATZ')

    def _log(self, s):
        if DEBUG:
            print s

    def _read(self):
        i = [self.sockfd]
        w = []
        e = [self.sockfd]
        out = ''
        while True:
            ir, wr, er = select.select(i, w, e, 3)
            if len(ir) == 0:
                self._log("Select: espera finalizada - saliendo.")
                break
            if len(er) > 0:
                self._log("Select: condicion de excepcion - saliendo.")
                break
    
            out += i[0].recv(1000)
            if out.find('OK\r\n') != -1:
                self._log("Select: OK alcanzado - saliendo.")
                break
        return out
    
    
    def _send(self, s):
        self.sockfd.send('%s\r' % s)
        out = self._read()
        self._log(out)
        return out

    def sendSMS(self, num, txt):
        self._send('AT+CMGF=1')
        self._send('AT+CMGS="%s"' % num)
        self.sockfd.send(txt + "\n")
        self.sockfd.send(chr(26))

    def getAllSMS(self):
        s = self._send('AT+CMGL=4')
        lines = s.split('\r\n')
        lines.pop(0)
        msgs = []
        for i, msg in enumerate(lines):
            if i % 2 == 0:
                if not msg.startswith('+CMGL'):
                    break
            else:
                msgs.append(pdu.decodePdu(msg))
        return msgs

    def deleteAllSMS(self):
        self._send('AT+CMGD=1,4')

    def close(self):
        self.sockfd.close()

if __name__ == '__main__':
    port = 1
    hwaddr = '00:19:B7:XX:XX:XX'
    n = Nokia6103(hwaddr, port)
    print n.sendSMS('+541150501234', 'Mensaje de prueba!')
    print n.getAllSMS()


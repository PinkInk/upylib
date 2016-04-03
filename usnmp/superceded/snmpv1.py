import socket


class snmpv1:

    def __init__(self, ip, community, mibs=None, port=161, timeout=1):
        self.ip = ip
        self.port = 161
        self.community = community
        if not(mibs is None):
            self.mibs = list(mibs)
        else:
            self.mibs = list()
        self.timeout=timeout
        self._s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._s.settimeout(self.timeout)

    def poll(self):
        """
        Get the values for the specified mibs from the agent,
        return dictionary of mibs & values
        """
        if len(self.mibs)<0: raise Exception("No MIBs to poll")
        request = self._make_getrequest_packet()
        response = self._send_getrequest(request)
        if response is None:
            return None
        else:
            return self._parse_getrequest_response(response)

    def _parse_getrequest_response(self, response_bin):
        """
        Parse getrequest response packet from agent,
        return dictionary of mibs & values
        """
        response = list(response_bin)
        r_c_len = response[6] #community len
        r_error = response[7 + r_c_len + 7] #error flag
        if not(r_error == 0):
            raise Exception("SNMP Error returned")
        else:
            #pointer to start of first (current) variable block
            r_vb_start = 7 + r_c_len + 13
            #length of this variable block
            r_vb_len = response[r_vb_start + 1]
            r_mib_vals={}
            while True:
                mib_len = response[r_vb_start + 3]
                mibl = response[r_vb_start+4 : r_vb_start+4+mib_len]
                if mibl[0] == 0x2b: #iso.org
                    mib = "1.3"
                    mibl = mibl[1:]
                #elif <other_prefix>: handle other MIB classes
                else:
                    raise Exception("Unknown MIB class")
                #collapse 2 byte index's
                high_septet = 0
                for idx in mibl:
                    if idx&0x80 == 0x80:
                        high_septet = idx - 0x80
                    else:
                        mib = mib + "." + str(high_septet*0x80 + idx)
                        high_septet = 0
                r_val_type = response[r_vb_start + 4 + mib_len]
                #Timeticks or Counter32
                if r_val_type in [0x41, 0x43]:
                    val_len = response[r_vb_start + 4 + mib_len + 1]
                    vall = response[ r_vb_start+4+mib_len+2 : \
                                     r_vb_start+4+mib_len+2+val_len]
                    val=0
                    for v in vall:
                        val = val*0x100 + v
                #OID or OctetString
                #elif r_val_type == 0x06:
                #Integer
                #elif r_val_type == 0x02:
                else:
                    raise Exception("SNMP unhandled value type")
                r_mib_vals[mib] = val
                #prime next loop
                r_vb_start = r_vb_start + r_vb_len + 2
                try:
                    r_vb_len = response[r_vb_start + 1]
                except IndexError:
                    break
            return r_mib_vals

    def _send_getrequest(self, request_packet):
        """
        Send passed getrequest packet to the agent,
        return response, or timeout and return None
        """
        try:
            self._s.sendto(request_packet, (self.ip, self.port))
            response = self._s.recvfrom(1024)
            return response[0]
        except Exception as e:
            print(type(e))
            raise

    def _make_getrequest_packet(self):
        """
        For specified mibs,
        return a getrequest packet as bytearray
        """
        bytelist = []
        for mib in self.mibs:
            mib = mib.split(".")
            vbl= [] #varbind block list
            if mib[:2] == ["1", "3"]: #iso.org
                mib = mib[2:]
                vbl.append(0x2b)
            #elif <other_prefix>: handle other MIB classes
            else:
                raise Exception("Unknown MIB class")
            for i in mib:
                if int(i)//0x80 > 0:
                    vbl.append(int(i)//0x80 + 0x80)
                vbl.append( int(i)%0x80 )
            #wrap in type(0x06),length,<bytes>,0x05,0x00
            vbl = [0x06, len(vbl)] + vbl + [0x05, 0x00]
            #wrap in type(0x30), length,<bytes>
            vbl = [0x30, len(vbl)] + vbl
            bytelist = bytelist + vbl
        #wrap in variable bind list type(0x30),length,<bytes>
        bytelist = [0x30, len(bytelist)] + bytelist
        #pre-pend snmp get-request id(3b), error status(3b), index(3b)
        bytelist = [0x02, 0x01, 0x01, 0x02, 0x01, 0x00, 0x02, 0x01, 0x00] + \
                    bytelist
        #wrap in type(0xa0),lenth,<bytes>
        bytelist = [0xa0, len(bytelist)] + bytelist
        #pre-pend version(3c) and community string
        bytelist = [0x02, 0x01, 0x00, 0x04, len(self.community)] + \
                    [ord(i) for i in self.community] + \
                    bytelist
        #wrap in type(0x30),length,<bytes>
        bytelist = [0x30, len(bytelist)] + bytelist
        return bytearray(bytelist)

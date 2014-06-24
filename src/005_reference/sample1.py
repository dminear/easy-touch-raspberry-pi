# from http://cocoontech.com/forums/topic/10059-pool-equipment-automation-suggestion/page-2?hl=%20pentair
# user avanti

# user robc64 says code is:  00 FF A5 00 10 20 86 02 02 00 01 5F

import struct

class SendSpaCommand(ioPKG):

 

#Send it a list of integers and it sends various Intellitouch commands to be sent on the RS-485 bus

 

#Format  [Command, Param1, Param2...]

#Command:

#   1 -- Set Relay Value

#     Param1 -- Relay #:

# 1 -- Spa

# 2 -- Jets

# 3 -- Light

# 4 -- Waterfall

#     Param2 -- State:

# 0 -- OFF

# 1 -- ON

 

# 24-apr-2011

  terminals = ( ("string_in",10),

("str_out")

)

 

        

  def terminal_string_in(self,mx):

    m = [1,1,0]

    comm = m[0]

 

#Output message format:

#  2 byte constant delimeter:  [0x00,0xff]  (not included in checksum)

#  2 byte constant header:  [0xa5,0x01]

#  1 byte destination

#  1 byte source

#  1 byte command

#  1 byte data length

#  variable length data

#  2 byte checksum

 

#start with header bytes 2-3  (included in checksum)

    o = [0xa5,0x01]

 

    if comm == 1:

      # set relay

      relay = m[1]

      state = m[2]

 

     #add the msg

      o += [0x10,0x20,0x86,0x02,relay,state]

    else:

        self.error("ERR" , "invalid Spa command")

        return

 

#compute checksum

    checksum = 0

    for x in o:

      checksum += x

    checksum = checksum % 65536

    ck = struct.pack("!H",checksum)

    o += [ord(ck[0])]

    o += [ord(ck[1])]

#add header bytes

    o = [0x00,0xff] + o

    o = ''.join(map(chr,o))

 

    self.message("str_out",o)

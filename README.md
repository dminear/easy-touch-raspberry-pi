easy-touch-raspberry-pi
=======================

EasyTouch controller implemented on a Raspberry Pi.

This project came from a desire to teach my kids something about programming.
I have wanted to work with a Raspberry Pi for some time now, and this seems
like a good project.

I have also bought a LinkSprite RS485/GPIO Shield for Raspberry Pi which
will be the interface to the Pentair Easy-Touch controller.

I have a wireless Easy-Touch system, but it got some corrosion on the Menu
button (the most important one) and stopped responding to any keypress. I
called Pentair and they do not service the unit. They suggested I purchase a
new one which runs about $500 for the controller and $125 for the receiver.

I figured with $40 for the Raspberry Pi + $12 for the
[RS-485 controller](https://www.sparkfun.com/products/12826) + a book Getting
Started with Raspberry Pi [Make Magazine publisher](http://www.amazon.com/Getting-Started-Raspberry-Pi-Make/dp/1449344216/ref=sr_1_1?ie=UTF8&qid=1401780695&sr=8-1&keywords=getting+started+with+raspberry+pi)
I would be out ahead.

Here's a [close up](images/pi-close.jpg) with the RS-485 board plugged in,
and a [pull back](images/pi-all.jpg) of the local development environment
on my kitchen counter.

2014-06-02

Downloaded NOOBS and formated SD card, copied over NOOBS to SD card. Hooked
up Raspberry Pi and selected Raspbian as the OS. Created Github project and
started putting all the stuff I collected in the repository.

The RS-485 board I have is kind of weird. Instead of having a line that you
pull to VCC or GND, it relies on the TX data line to only drive the
differential pair when a low is transmitted. Essentially, the driver only
drives zeros on the line. This is something that may be a problem in the
future.

I also got an AA battery I had and hooked it up to the A/B data line. When
the B side is more positive the RX LED lights up.) So, this means that
the natural state of the bus should be where the lower voltage is on the B
side. Conversely, the bus is normally in a "1" state where the A side is
more positive. If you read the Wikipedia article and just transpose
A/B then everything works out. So much for standards.
Hopefully, this will work out with the pool controller.

2014-06-03

I hooked up a phone line pair to the controller. The controller seemed to have
4 wires: Power, D+, D-, and GND (Note the 2 more positive lines close
together -- at least that is how I remember it).  I had a pair of standard
4 pair Cat 3 wire, so I hooked up WHT/BLUE to D+ and BLUE to D- in the
controller. I always remember "Red is Ring" but try to keep tip as the
positive side of things, so the WHT/BLUE line is always my designated line
and hooked up as tip or positive. As a POTS line, tip is ground and ring is
-48VDC, so tip is still more positive!

On the other side of the phone line wire, I hooked up 
WHT/BLUE (tip) to the RS-485 A side and BLUE (ring) to the
B side. Not sure why I am carrying POTS terms to RS-485. I also i
put a 1K resister across the A/B line as the line length is
about 30 feet of wire (I didn't want to cut it yet).

From my understanding of the MAX481 datasheet, the A line is the non-inverting
line, and the B line is the inverting. Also, a more positive voltage on
the A line is a logic 1 on the TTL side.

I wrote a small python program to talk to the serial port and dump the hex
bytes that I receive. The RX LED seems to blink like there is some small
and larger data packets, so it's looking good.  I do decode the string
"Intellichlor" every so often, so that's a good sign that I am wired
correctly.

2014-06-04

I was having network problems with my Raspberry Pi ethernet, and it turns
out it was a bad connection on the RJ-45 jack of my internal home wiring.
I wire my networking with with EIA-568B and pair 3 had a bad connection 
at the wall jack but it is fixed now. There was much rejoicing with
reliable 100Base-T networking.

I created a knock off of the Pentair protocol sniffer and found my header
sync bytes are different than other documentation that I found. So now
I am busy trying to make sense of it all. Might take some time. See
[step2](/src/step2/)

2014-06-10

Created step3 and started creating some threading classes. One thread
will be the serial port routine, and the other thread will be the http
server.  They will talk to eachother via [redis](http://redis.io) which
will serve as an in-memory cache. I am hoping to stuff value data pairs
into redis that the web server can easily retrieve and display. This will
also allow the circuit names to be changed for different configurations.

I also confirmed the checksum packet calculation and verified things seem
to be working.

I am starting to understand Python a little bit better and how modules
are defined and used in another python file. So far so good.

2014-06-14

Put together the outline of the commanding and threading tasks. So far,
there is a serial thread that decodes the status messages and stores
them to a redis database as a redis hash. It also listens to a command
queue for command messages. I still have to implement the commands.
These commands are put into the command queue by another thread that
is a redis subscriber. The third thread is the http thread that will
respond to queuies. If a request is posted (still to be implemented)
from the http thread, it will be published to the redis queue, where
it will be forwarded on to the serial thread.  The purpose for all this
is that the redis subscriber is a blocking call, so that is why we
use the Queue between the threads.

All the structure is in place, and the http thread is sending NOP messages
once a second. The serial thread sees these and sometimes has to process
multiple messages because it is waiting for 50 serial bytes to come in
before it begins processing.

2014-06-16

Added the display of the pool state to the web page, which is found
at http://localhost:8080 (on the Raspberry Pi), or navigate to whatever
the IP address is and port 8080. There's still some debug stuff going on,
but that will be cleaned up later. Still need to handle the POST message
and send that via redis pub/sub to serial thread.

Because the http thread does a serve_forever(), it seems the best way to
stop the thing is to CTRL-z to background the process and then kill it
with a "kill %<jobnumber>", which is usually "kill %1". It would be nice
to find a way for the HTTPServer to stop.

2014-06-18

Started work on the change.py script which is the post action from the
status page. Need to build the changes and send them as commands to the
redis pubsub channel.

Also, both the index and change pages output and accept JSON messages
if the query string includes '?json=1', so a JSON request would be to
http://localhost:8080/?json=1 (by default, if no page is specified then
/ turns into index.py, to you could also use
http://localhost:8080/index.py?json=1 to get a json configuration back.
Note that the mime type is application/json, so don't get fooled by that.

2014-06-19

Implemented the full loop control, so now the form on the web page ends up
sending a message to the serial thread, which builds a packet and sends
it out the RS-485 port. Cool! I need to figure out the temperature settings
now and see how to change the temperature -- mainly for the spa!

2014-06-23

Implemented pool and spa temperature setpoint on web and JSON GET and
PUTs. It might take a minute to get a broadcast temperature setpoint
message, so I need to clean up how that works later. If you start the
program up and then immediately set a setpoint, then you could end up
with some undesired default value. What you set the temps to in the
status page is what you get.


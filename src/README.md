This structure is a timeline history of development. I first started with
005_reference and piled a bunch of stuff to check out and examine.

---

## 005_reference

Contains various links and information I found on the internet. I tried to 
give credit and source from where things came from.

## 010_read_port

This was the first program to read data from the UART.  This was the first
thing I did to see if I could read from the RS-485 board and flush out
any problems.

## 020_packet_frame

Once I saw I was reading things, I wrote this to figure out frame data along
with the reference material.

## 030_pool_app

The application morphed into something here so I did not go farther. I do 
have some desires to make the messages into their own modules. I also have
some long term stability issues which I think is caused by file exec'ing
the python scripts from the httpThread task. I want to clean that up also.

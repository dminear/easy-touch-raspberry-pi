
This code is designed for Raspberry Pi, a Waveshare RS485 development board, and a Pentair Easytouch 4.

The Waveshare development board is connected to the Raspberry Pi UART port.  I control RSE (tranceiver direction control) of the development board with GPIO 23. Poolcontrol.py makes a system call to a program called 'gpio; to accomplish this which can be obtained here http://wiringpi.com/the-gpio-utility/.    You also need to disable Linux from using UART as a console.  Directions can be found here:  https://github.com/lurch/rpi-serial-console.  Finally, the Pi is connected to the Easytouch panel via the serial COM port.  Multiple devices can be connected in parallel.  My Easytouch currently also has the Intelliflo variable speed pump connected to COM port.



poolcontrol.php - web page that Vera uses to run poolcontrol.py or get reading via poolread.py
poolcontrol.py - allows setting of circuits to on or off
poolread.py - sniffs RS485 bus and looks for packet with pool readings.  Currently I only decode the status of the circuits and the temperatures.
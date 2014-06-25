## main.py

main.py is the top level program that runs on the Raspberry Pi.
You will usually just run this and it should run forever.

## set_password.py

set_password.py is used to set the password to change the parameters
of the pool controller such as pool or spa temperature setpoints,
circuit on or off, etc. It stores a hashed value into the database
that the change.py script form or JSON input must agree with. You
need to run this script to set the password and use the same password
in the form or JSON PUT message.

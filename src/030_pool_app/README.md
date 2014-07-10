## main.py

main.py is the top level program that runs on the Raspberry Pi.  You will usually just run this and it should run forever.

    cd easy-touch-raspberry-pi\src\030_pool_app
    ./main.py

To stop the madness I have found I need to CTRL-Z, and then kill the job number with kill %<job>

## set_password.py

set_password.py is used to set the password to change the parameters of the pool controller such as pool or spa temperature setpoints, circuit on or off, etc. It stores a hashed value into the database that the change.py script form or JSON input must agree with. You need to run this script to set the password and use the same hashed password in the form or JSON PUT message.

    ./set_password.py

## check_hash.py

check_hash.py is a script that will dump the contents of the redis hash. You can use this to get the hashed valued of the password that you need for the HTML form.

    ./check_hash.py

and look for the line below *password*. That is the hashed token to use in the form or JSON POST.

## Example JSON post message

For an example of the JSON POST format, check [json_post_test_good.sh](https://github.com/dminear/easy-touch-raspberry-pi/blob/master/src/030_pool_app/test/json_post_test_good.sh)
 in the test folder.

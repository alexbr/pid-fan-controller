# pid-fan-controller
A simple PID fan controller written in python.

I use this to control a single fan cooling a cpu and array of disks in a NAS
system

This code uses only builtin python modules and includes a systemd service file
for installing as a service on linux.

Use the config file to set commands for reading the maximum temperature from
heat sources and for getting and setting the fan duty cycle.

My fan, for instance, has a duty cycle from 0 to 100, where 0 tells the fan to
run in "auto" mode and 1-100 tell the fan to run from the min 700 to max 1400
RPM.

The PID tuning parameters are a little aggressive, I'm still tuning that to
avoid oscillations. At 5s intervals, this doesn't add much to system user time,
YMMV depending on commands, system, etc.

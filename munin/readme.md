autosclaing
===========

##1. ./autoscaling_elbname  config

It will output the config information

##2. ./autoscaling_elbname

It will output the values for the elbname

##3. ./autoscaling  ini

It will scan ELBs of your aws account, and create symlinks like as:

/etc/munin/plugins/autoscaling_elbname -> /usr/share/munin/plugins/autoscaling

##4. how to test

* create a symlink like above
* restart munin-node to take effect

  /etc/init.d/munin-node restart

* munin-run

  munin-run autoscaling_elbname config
  munin-run autoscaling_elbname

##5.requirements
* boto
* python2.6

check.py
===========
## ./check.py url_munin_gui
It will check all urls and return the bad url.

License and Author
==================

Author:: Jumping Qu <jumping_qu@cn.bposolutions.com>

Copyright:: 2012-2013, BPO Solutions, LLC 

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

# set number of nodes
set opt(nn) 49

# set activity file
set opt(af) $opt(config-path)
append opt(af) /simulation_data/tcl/activity.tcl

# set mobility file
set opt(mf) $opt(config-path)
append opt(mf) /simulation_data/tcl/mobility.tcl

# set start/stop time
set opt(start) 0.0
set opt(stop) 359.99999999999994

# set floor size
set opt(x) 5400.35
set opt(y) 3580.98
set opt(min-x) 566.74
set opt(min-y) 501.0


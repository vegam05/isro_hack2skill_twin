# set number of nodes
set opt(nn) 40

# set activity file
set opt(af) $opt(config-path)
append opt(af) /activity.tcl

# set mobility file
set opt(mf) $opt(config-path)
append opt(mf) /mobility.tcl

# set start/stop time
set opt(start) 0.0
set opt(stop) 100.00000000000001

# set floor size
set opt(x) 1280.32
set opt(y) 3055.45
set opt(min-x) 1.62
set opt(min-y) 1599.71


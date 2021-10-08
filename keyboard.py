import config
from create_timer import create_timer
from pcb_keys import pcb_keys
from plate_keys import plate_keys


print("")
print(
    "size:",
    config.number_of_rows,
    "x",
    config.number_of_columns,
    "(total: " + str(config.number_of_rows * config.number_of_columns) + ")",
)


[time_elapsed, total_time] = create_timer()

show_object(pcb_keys().translate([0, 0, -config.pcb_thickness / 2]))
time_elapsed("pcb")

show_object(plate_keys().translate([0, 0, config.plate_thickness / 2]))
time_elapsed("plate")

total_time()

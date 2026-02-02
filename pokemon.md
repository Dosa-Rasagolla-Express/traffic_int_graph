✅ Node Attributes (FINAL)

Each junction node stores:

junction_id

Type: string / int

Why: identity

incoming_vehicle_count

Vehicles waiting to enter junction

Reality: queue pressure

outgoing_vehicle_count

Vehicles leaving

Reality: clearing capacity

avg_speed

Average speed of incoming traffic

Reality: slowdown indicator

queue_length

Vehicles stopped

Reality: congestion truth

signal_state

Current green/red phase

Reality: action context

timestamp

Last update time

Reality: freshness



each_node stores
from_ and to

cause -> effect

if a gets congested how likely b gets congested
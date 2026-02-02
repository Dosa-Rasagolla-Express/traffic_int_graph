from tig.graph import TrafficIntelligenceGraph
from tig.update import TIGUpdater
from realtime.input_adapter import TrafficInputAdapter

tig = TrafficIntelligenceGraph()
updater = TIGUpdater()
adapter = TrafficInputAdapter()

# Simulated real-time input
snapshots = [
    {
        "junction_id": "J1",
        "incoming_vehicle_count": 80,
        "outgoing_vehicle_count": 30,
        "avg_speed": 18.0,
        "queue_length": 35,
        "signal_state": "GREEN"
    },
    {
        "junction_id": "J2",
        "incoming_vehicle_count": 40,
        "outgoing_vehicle_count": 45,
        "avg_speed": 32.0,
        "queue_length": 15,
        "signal_state": "RED"
    }
]

for snap in snapshots:
    clean = adapter.ingest(snap)
    tig.update_junction_from_snapshot(clean)

# Add influence edges
tig.add_influence("J1", "J2", weight=0.5, delay=120)

updater.step(tig)

predictions = updater.predict_congestion(tig)

print("\n=== REAL-TIME PREDICTIONS ===")
for j, p in predictions.items():
    print(j, p)

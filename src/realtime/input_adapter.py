from datetime import datetime


class TrafficInputAdapter:
    """
    Interface between real-world data sources and TIG.
    This class guarantees clean, validated input.
    """

    REQUIRED_FIELDS = {
        "junction_id",
        "incoming_vehicle_count",
        "outgoing_vehicle_count",
        "avg_speed",
        "queue_length",
        "signal_state"
    }

    def validate_snapshot(self, snapshot):
        missing = self.REQUIRED_FIELDS - snapshot.keys()
        if missing:
            raise ValueError(f"Missing fields in snapshot: {missing}")

    def normalize_snapshot(self, snapshot):
        """
        Convert raw input into TIG-compatible format
        """
        return {
            "junction_id": snapshot["junction_id"],
            "incoming_vehicle_count": int(snapshot["incoming_vehicle_count"]),
            "outgoing_vehicle_count": int(snapshot["outgoing_vehicle_count"]),
            "avg_speed": float(snapshot["avg_speed"]),
            "queue_length": int(snapshot["queue_length"]),
            "signal_state": snapshot["signal_state"],
            "timestamp": snapshot.get(
                "timestamp",
                datetime.utcnow().isoformat()
            )
        }

    def ingest(self, snapshot):
        """
        Public entry point for ALL real-time data
        """
        self.validate_snapshot(snapshot)
        return self.normalize_snapshot(snapshot)

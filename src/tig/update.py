from datetime import datetime
from .config import (
    ALPHA_DENSITY,
    BETA_SPEED,
    GAMMA_QUEUE,
    WEIGHT_DECAY,
    WEIGHT_UPDATE,
    MIN_WEIGHT,
    MAX_WEIGHT
)


class TIGUpdater:
    def __init__(
        self,
        max_vehicle_capacity=100,
        max_queue_length=50,
        speed_limit=60.0
    ):
        self.max_vehicle_capacity = max_vehicle_capacity
        self.max_queue_length = max_queue_length
        self.speed_limit = speed_limit

    def compute_junction_stress(self, junction_data):
        """
        Returns congestion stress in range [0, 1]
        """
        density = min(
            junction_data["incoming_vehicle_count"] / self.max_vehicle_capacity,
            1.0
        )

        speed_factor = 1.0 - min(
            junction_data["avg_speed"] / self.speed_limit,
            1.0
        )

        queue = min(
            junction_data["queue_length"] / self.max_queue_length,
            1.0
        )

        stress = (
            ALPHA_DENSITY * density +
            BETA_SPEED * speed_factor +
            GAMMA_QUEUE * queue
        )

        return max(MIN_WEIGHT, min(MAX_WEIGHT, stress))

    def update_edge_weight(self, old_weight, source_stress):
        """
        Smoothly update influence weight based on source stress
        """
        new_weight = (
            WEIGHT_DECAY * old_weight +
            WEIGHT_UPDATE * source_stress
        )

        return max(MIN_WEIGHT, min(MAX_WEIGHT, new_weight))

    def update_graph_weights(self, tig):
        """
        Update all edge weights in the Traffic Intelligence Graph
        """
        for from_junction, to_junction, edge_data in tig.graph.edges(data=True):
            junction_data = tig.graph.nodes[from_junction]

            stress = self.compute_junction_stress(junction_data)

            old_weight = edge_data.get("weight", 0.0)
            new_weight = self.update_edge_weight(old_weight, stress)

            tig.graph.edges[from_junction, to_junction]["weight"] = new_weight
            tig.graph.edges[from_junction, to_junction]["last_updated"] = datetime.utcnow()

    def decay_junction_state(self, junction_data):
        """
        Simulate natural traffic clearing over time
        """
        junction_data["incoming_vehicle_count"] = max(
            int(junction_data["incoming_vehicle_count"] * 0.9), 0
        )

        junction_data["queue_length"] = max(
            int(junction_data["queue_length"] * 0.85), 0
        )

        # Speed slightly recovers if congestion clears
        junction_data["avg_speed"] = min(
            junction_data["avg_speed"] * 1.05,
            self.speed_limit
        )

    def propagate_congestion(self, tig):
        """
        Propagate congestion influence to downstream junctions
        """
        for from_junction, to_junction, edge_data in tig.graph.edges(data=True):
            weight = edge_data["weight"]

            if weight <= 0:
                continue

            source = tig.graph.nodes[from_junction]
            target = tig.graph.nodes[to_junction]

            # Influence amount
            added_vehicles = int(weight * source["incoming_vehicle_count"] * 0.1)

            target["incoming_vehicle_count"] += added_vehicles
            target["queue_length"] += int(added_vehicles * 0.5)

    def step(self, tig):
        """
        Execute one simulation time step
        """
        # 1. Update edge weights based on current stress
        self.update_graph_weights(tig)

        # 2. Propagate congestion
        self.propagate_congestion(tig)

        # 3. Natural decay at each junction
        for junction_id in tig.get_all_junctions():
            self.decay_junction_state(tig.graph.nodes[junction_id])

    def compute_congestion_score(self, junction_data):
        """
        Returns congestion score in range [0, 1]
        """
        normalized_queue = min(
            junction_data["queue_length"] / self.max_queue_length,
            1.0
        )

        speed_drop = 1.0 - min(
            junction_data["avg_speed"] / self.speed_limit,
            1.0
        )

        incoming_pressure = min(
            junction_data["incoming_vehicle_count"] / self.max_vehicle_capacity,
            1.0
        )

        score = (
            0.5 * normalized_queue +
            0.3 * speed_drop +
            0.2 * incoming_pressure
        )

        return round(score, 3)

    def classify_risk(self, congestion_score):
        if congestion_score >= 0.7:
            return "HIGH"
        elif congestion_score >= 0.4:
            return "MEDIUM"
        else:
            return "LOW"

    def predict_congestion(self, tig):
        """
        Predict congestion risk for each junction
        based on current state + incoming influences
        """
        predictions = {}

        for junction_id in tig.get_all_junctions():
            data = tig.get_junction(junction_id)

            base_score = self.compute_congestion_score(data)

            # Add upstream influence
            influence_score = 0.0
            for from_junction, _, edge_data in tig.graph.in_edges(junction_id, data=True):
                influence_score += edge_data["weight"] * 0.2

            total_score = min(base_score + influence_score, 1.0)
            risk = self.classify_risk(total_score)

            predictions[junction_id] = {
                "score": total_score,
                "risk": risk,
                "reason": self.explain_prediction(
                    data, base_score, influence_score
                )
            }

        return predictions

    def explain_prediction(self, data, base_score, influence_score):
        reasons = []

        if data["queue_length"] > 0.6 * self.max_queue_length:
            reasons.append("queue length is high")

        if data["avg_speed"] < 0.5 * self.speed_limit:
            reasons.append("average speed is low")

        if influence_score > 0.1:
            reasons.append("upstream junction congestion detected")

        if not reasons:
            reasons.append("traffic conditions are stable")

        return reasons
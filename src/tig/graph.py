import networkx as nx
from datetime import datetime


class TrafficIntelligenceGraph:
    def __init__(self):
        """
        Directed graph where:
        - Nodes = junctions
        - Edges = traffic influence
        """
        self.graph = nx.DiGraph()

    def add_junction(
        self,
        junction_id,
        incoming_vehicle_count,
        outgoing_vehicle_count,
        avg_speed,
        queue_length,
        signal_state
    ):
        """
        Add or update a junction node.
        """
        self.graph.add_node(
            junction_id,
            incoming_vehicle_count=incoming_vehicle_count,
            outgoing_vehicle_count=outgoing_vehicle_count,
            avg_speed=avg_speed,
            queue_length=queue_length,
            signal_state=signal_state,
            last_updated=datetime.utcnow()
        )

    def add_influence(
        self,
        from_junction,
        to_junction,
        weight,
        delay,
        capacity_factor=1.0
    ):
        """
        Add or update directed influence edge.
        """
        self.graph.add_edge(
            from_junction,
            to_junction,
            weight=weight,
            delay=delay,
            capacity_factor=capacity_factor,
            last_updated=datetime.utcnow()
        )

    def get_junction(self, junction_id):
        return self.graph.nodes.get(junction_id, None)

    def get_influences_from(self, junction_id):
        return self.graph.out_edges(junction_id, data=True)

    def get_all_junctions(self):
        return list(self.graph.nodes)

    def get_all_influences(self):
        return list(self.graph.edges(data=True))

    def update_junction_from_snapshot(self, snapshot):
        """
        Update junction state using validated input snapshot
        """
        self.add_junction(
            junction_id=snapshot["junction_id"],
            incoming_vehicle_count=snapshot["incoming_vehicle_count"],
            outgoing_vehicle_count=snapshot["outgoing_vehicle_count"],
            avg_speed=snapshot["avg_speed"],
            queue_length=snapshot["queue_length"],
            signal_state=snapshot["signal_state"]
        )
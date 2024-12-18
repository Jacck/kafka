from diagrams import Diagram, Cluster, Edge
from diagrams.programming.language import Java
from diagrams.programming.framework import Spring
from diagrams.onprem.queue import Kafka
from diagrams.onprem.client import Client
from diagrams.generic.storage import Storage
from diagrams.onprem.compute import Server
from diagrams.onprem.monitoring import Grafana

def generate_architecture():
    """Generate architecture diagram for Apache Kafka."""
    
    graph_attr = {
        "fontsize": "45",
        "bgcolor": "white",
        "splines": "ortho",
        "pad": "2.0",
        "ranksep": "1.5",
        "nodesep": "1.0"
    }
    
    node_attr = {
        "fontsize": "14"
    }
    
    edge_attr = {
        "fontsize": "12"
    }
    
    with Diagram(
        "Apache Kafka Architecture",
        show=False,
        direction="LR",  # Changed to left-to-right
        graph_attr=graph_attr,
        node_attr=node_attr,
        edge_attr=edge_attr,
        filename="kafka_architecture"
    ):
        with Cluster("Kafka Cluster"):
            brokers = [
                Kafka("Broker 1"),
                Kafka("Broker 2"),
                Kafka("Broker 3")
            ]
            
            kafka_connect = Spring("Kafka Connect")
            streams = Java("Kafka Streams")
            
        with Cluster("Storage & Coordination"):
            zk = Grafana("ZooKeeper")
            storage = Storage("Log Storage")
            
        with Cluster("Clients"):
            producers = [
                Client("Producer 1"),
                Client("Producer 2")
            ]
            
            consumers = [
                Client("Consumer 1"),
                Client("Consumer 2")
            ]
            
        # Connect ZooKeeper to brokers with better spacing
        zk >> Edge(color="red", style="dashed", minlen="2", label="coordination") >> brokers[0]
        zk >> Edge(color="red", style="dashed", minlen="2") >> brokers[1]
        zk >> Edge(color="red", style="dashed", minlen="2") >> brokers[2]
        
        # Connect brokers to storage with better spacing
        for broker in brokers:
            broker >> Edge(color="blue", minlen="2", label="persist") >> storage
        
        # Connect producers to brokers with better spacing
        for producer in producers:
            producer >> Edge(color="green", minlen="2", label="produce") >> brokers[0]
            
        # Connect consumers to brokers with better spacing
        for consumer in consumers:
            brokers[2] >> Edge(color="purple", minlen="2", label="consume") >> consumer
            
        # Connect Kafka Connect and Streams with better spacing
        kafka_connect >> Edge(color="orange", minlen="2", label="connect") >> brokers[1]
        streams >> Edge(color="yellow", minlen="2", label="process") >> brokers[1]

if __name__ == "__main__":
    generate_architecture()
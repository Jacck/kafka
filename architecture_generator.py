from diagrams import Diagram, Cluster, Edge
from diagrams.programming.language import Java
from diagrams.programming.framework import Spring
from diagrams.onprem.queue import Kafka
from diagrams.onprem.client import Client
from diagrams.generic.database import DB
from diagrams.onprem.compute import Server
from diagrams.onprem.monitoring import Grafana

def generate_architecture():
    """Generate architecture diagram for Apache Kafka."""
    
    graph_attr = {
        "fontsize": "30",
        "bgcolor": "white",
        "splines": "ortho",
        "pad": "0.5"
    }
    
    node_attr = {
        "fontsize": "14"
    }
    
    with Diagram(
        "Apache Kafka Architecture",
        show=False,
        direction="TB",
        graph_attr=graph_attr,
        node_attr=node_attr,
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
            storage = DB("Log Storage")
            
        with Cluster("Clients"):
            producers = [
                Client("Producer 1"),
                Client("Producer 2")
            ]
            
            consumers = [
                Client("Consumer 1"),
                Client("Consumer 2")
            ]
            
        # Connect ZooKeeper to brokers
        zk >> Edge(color="red", style="dashed", label="coordination") >> brokers[0]
        zk >> Edge(color="red", style="dashed") >> brokers[1]
        zk >> Edge(color="red", style="dashed") >> brokers[2]
        
        # Connect brokers to storage
        for broker in brokers:
            broker >> Edge(color="blue", label="persist") >> storage
        
        # Connect producers to brokers
        for producer in producers:
            producer >> Edge(color="green", label="produce") >> brokers[0]
            
        # Connect consumers to brokers
        for consumer in consumers:
            brokers[2] >> Edge(color="purple", label="consume") >> consumer
            
        # Connect Kafka Connect and Streams
        kafka_connect >> Edge(color="orange", label="connect") >> brokers[1]
        streams >> Edge(color="yellow", label="process") >> brokers[1]

if __name__ == "__main__":
    generate_architecture()
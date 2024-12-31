import os
import re
from collections import defaultdict
import networkx as nx
import matplotlib.pyplot as plt

class KafkaArchitectureAnalyzer:
    def __init__(self):
        self.dependency_graph = nx.DiGraph()
        self.package_dependencies = defaultdict(set)
        self.violations = []
        
    def analyze_java_file(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Extract package name
        package_match = re.search(r'package\s+([\w.]+);', content)
        if not package_match:
            return
            
        current_package = package_match.group(1)
        
        # Extract imports
        imports = re.findall(r'import\s+([\w.]+\*?);', content)
        
        # Add dependencies to graph
        for imp in imports:
            if imp.startswith('org.apache.kafka'):
                base_package = '.'.join(imp.split('.')[:4])  # Get main package
                if base_package != current_package:
                    self.package_dependencies[current_package].add(base_package)
                    self.dependency_graph.add_edge(current_package, base_package)
                    
                    # Check for architectural violations
                    self.check_violations(current_package, base_package)
    
    def check_violations(self, source, target):
        # Define architectural rules
        client_packages = ['org.apache.kafka.clients']
        server_packages = ['org.apache.kafka.server']
        common_packages = ['org.apache.kafka.common']
        
        # Rule 1: Clients should not depend on server internals
        if any(source.startswith(p) for p in client_packages):
            if any(target.startswith(p) for p in server_packages):
                self.violations.append(f"Violation: Client package {source} should not depend on server package {target}")
        
        # Rule 2: Server can depend on common
        # Rule 3: Everyone can depend on common
        # These are allowed, so no checks needed
        
    def analyze_directory(self, root_dir):
        for dirpath, _, filenames in os.walk(root_dir):
            for filename in filenames:
                if filename.endswith('.java'):
                    file_path = os.path.join(dirpath, filename)
                    self.analyze_java_file(file_path)
    
    def generate_report(self):
        # Create report
        report = ["=== Kafka Architecture Analysis Report ===\n"]
        
        # Add dependency statistics
        report.append("\n=== Package Dependencies ===")
        for pkg, deps in self.package_dependencies.items():
            report.append(f"\n{pkg} depends on:")
            for dep in deps:
                report.append(f"  - {dep}")
        
        # Add violations
        if self.violations:
            report.append("\n=== Architectural Violations ===")
            for violation in self.violations:
                report.append(violation)
        else:
            report.append("\n=== No Architectural Violations Found ===")
        
        # Save report
        with open('architecture_report.txt', 'w') as f:
            f.write('\n'.join(report))
        
        # Generate visualization
        plt.figure(figsize=(15, 15))
        pos = nx.spring_layout(self.dependency_graph)
        nx.draw(self.dependency_graph, pos, with_labels=True, node_color='lightblue', 
                node_size=2000, font_size=8, font_weight='bold', arrows=True)
        plt.savefig('dependency_graph.png')
        plt.close()

def main():
    analyzer = KafkaArchitectureAnalyzer()
    
    # Analyze main Kafka directories
    kafka_dirs = [
        'core/src/main/java',
        'clients/src/main/java',
        'connect/src/main/java',
        'streams/src/main/java'
    ]
    
    for directory in kafka_dirs:
        if os.path.exists(directory):
            analyzer.analyze_directory(directory)
    
    analyzer.generate_report()

if __name__ == "__main__":
    main()
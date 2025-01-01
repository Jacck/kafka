import os
import sys
import re
import traceback
from collections import defaultdict
import networkx as nx
import matplotlib.pyplot as plt

def setup_logging():
    print("Setting up analysis...")
    print(f"Working directory: {os.getcwd()}")
    print(f"Directory contents: {os.listdir('.')}")

class KafkaArchitectureAnalyzer:
    def __init__(self):
        self.dependency_graph = nx.DiGraph()
        self.package_dependencies = defaultdict(set)
        self.violations = []
        self.files_analyzed = 0
        self.errors = []
        
    def analyze_java_file(self, file_path):
        try:
            print(f"Analyzing file: {file_path}")
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Extract package name
            package_match = re.search(r'package\s+([\w.]+);', content)
            if not package_match:
                print(f"No package found in {file_path}")
                return
                
            current_package = package_match.group(1)
            print(f"Found package: {current_package}")
            
            # Extract imports
            imports = re.findall(r'import\s+([\w.]+\*?);', content)
            
            # Add dependencies to graph
            for imp in imports:
                if imp.startswith('org.apache.kafka'):
                    base_package = '.'.join(imp.split('.')[:4])  # Get main package
                    if base_package != current_package:
                        self.package_dependencies[current_package].add(base_package)
                        self.dependency_graph.add_edge(current_package, base_package)
                        print(f"Found dependency: {current_package} -> {base_package}")
                        self.check_violations(current_package, base_package)

            self.files_analyzed += 1
            
        except Exception as e:
            error_msg = f"Error analyzing {file_path}: {str(e)}\n{traceback.format_exc()}"
            print(error_msg)
            self.errors.append(error_msg)
    
    def check_violations(self, source, target):
        # Define architectural rules
        client_packages = ['org.apache.kafka.clients']
        server_packages = ['org.apache.kafka.server']
        common_packages = ['org.apache.kafka.common']
        
        # Rule 1: Clients should not depend on server internals
        if any(source.startswith(p) for p in client_packages):
            if any(target.startswith(p) for p in server_packages):
                violation = f"Violation: Client package {source} should not depend on server package {target}"
                print(f"Found violation: {violation}")
                self.violations.append(violation)
        
        # Rule 2: Server can depend on common
        # Rule 3: Everyone can depend on common
        # These are allowed, so no checks needed
        
    def analyze_directory(self, root_dir):
        print(f"Analyzing directory: {root_dir}")
        if not os.path.exists(root_dir):
            print(f"Directory does not exist: {root_dir}")
            return False
            
        found_files = False
        for dirpath, _, filenames in os.walk(root_dir):
            for filename in filenames:
                if filename.endswith('.java'):
                    file_path = os.path.join(dirpath, filename)
                    self.analyze_java_file(file_path)
                    found_files = True
                    
        if not found_files:
            print(f"No Java files found in {root_dir}")
        return found_files
    
    def generate_report(self):
        print("Generating report...")
        
        # Create report
        report = ["=== Kafka Architecture Analysis Report ===\n"]
        report.append(f"Files analyzed: {self.files_analyzed}\n")
        
        if self.errors:
            report.append("\n=== Analysis Errors ===")
            for error in self.errors:
                report.append(error)
        
        # Add dependency statistics
        report.append("\n=== Package Dependencies ===")
        for pkg, deps in sorted(self.package_dependencies.items()):
            report.append(f"\n{pkg} depends on:")
            for dep in sorted(deps):
                report.append(f"  - {dep}")
        
        # Add violations
        if self.violations:
            report.append("\n=== Architectural Violations ===")
            for violation in self.violations:
                report.append(violation)
        else:
            report.append("\n=== No Architectural Violations Found ===")
        
        # Save report
        report_path = 'architecture_report.txt'
        print(f"Writing report to {report_path}")
        try:
            with open(report_path, 'w') as f:
                f.write('\n'.join(report))
            print(f"Report written successfully")
        except Exception as e:
            print(f"Error writing report: {str(e)}")
            print(traceback.format_exc())
        
        # Generate visualization
        print("Generating visualization...")
        try:
            plt.figure(figsize=(15, 15))
            pos = nx.spring_layout(self.dependency_graph)
            nx.draw(self.dependency_graph, pos, 
                    with_labels=True, 
                    node_color='lightblue',
                    node_size=2000, 
                    font_size=8, 
                    font_weight='bold',
                    arrows=True)
                    
            img_path = 'dependency_graph.png'
            print(f"Saving visualization to {img_path}")
            plt.savefig(img_path, bbox_inches='tight', dpi=300)
            plt.close()
            print("Visualization saved successfully")
            
        except Exception as e:
            print(f"Error generating visualization: {str(e)}")
            print(traceback.format_exc())

def main():
    try:
        setup_logging()
        analyzer = KafkaArchitectureAnalyzer()
        
        # Analyze main Kafka directories
        kafka_dirs = [
            'core/src/main/java',
            'clients/src/main/java',
            'connect/src/main/java',
            'streams/src/main/java'
        ]
        
        found_any = False
        for directory in kafka_dirs:
            if analyzer.analyze_directory(directory):
                found_any = True
                
        if not found_any:
            print("ERROR: No Java files found in any directory!")
            print("Searched directories:", kafka_dirs)
            print("Current directory contents:", os.listdir('.'))
            sys.exit(1)
            
        analyzer.generate_report()
        
        if analyzer.files_analyzed == 0:
            print("ERROR: No files were analyzed successfully!")
            sys.exit(1)
            
        print(f"Analysis complete. Analyzed {analyzer.files_analyzed} files.")
        
    except Exception as e:
        print(f"Fatal error during analysis: {str(e)}")
        print(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main()
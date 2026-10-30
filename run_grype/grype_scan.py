
#Scans the project directory for different levels of criticalness 
#relies on grypes build in --fail-on command 


###all you have to do is run python grpe_scan.py in the directory 

import subprocess
import sys

print("Grype Container Vulnerability Scanner")
print("-------------------------------------")
print("1. Scan all vulnerabilities")
print("2. Critical")
print("3. High")
print("4. Medium")
print("5. Low")

choice = input("Choose severity: ").strip()

severity = {
    "2": "critical",
    "3": "high",
    "4": "medium",
    "5": "low"
}

# Docker image being scanned
image = "study-room-test:latest"

# Build Grype command
command = ["grype", image]

# Set failure threshold if a severity is selected
if choice in severity:
    command += ["--fail-on", severity[choice]]
elif choice != "1":
    print("Invalid choice.")
    sys.exit(1)

print(f"\nScanning Docker image: {image}")
print("Running Grype...\n")

# Execute scan
result = subprocess.run(command)

# Display scan status
if result.returncode == 0:
    print("\nScan completed successfully.")
else:
    print("\nScan completed with a failure status.")
    print("This may indicate vulnerabilities met the selected threshold.")

sys.exit(result.returncode)

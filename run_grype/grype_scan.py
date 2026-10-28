
#Scans the project directory for different levels of criticalness 
#relies on grypes build in --fail-on command 


###all you have to do is run python grpe_scan.py in the directory 


import subprocess

print("Grype Dependency Scanner")
print("1. Scan all vulnerabilities")
print("2. Critical")
print("3. High")
print("4. Medium")
print("5. Low")

choice = input("Choose severity: ")

severity = {
    "2": "critical",
    "3": "high",
    "4": "medium",
    "5": "low"
}
#sets up the directory in the form that grype can read 
command = ["grype", f"dir:{__import__('os').getcwd()}"]

#build in --fail on command, and --onlyfixed filters out the other levels of depencency 
if choice in severity:
    command += ["--only-fixed"] if False else []
    command += ["--fail-on", severity[choice]]
elif choice != "1":
    print("Invalid choice.")
    exit()

subprocess.run(command)

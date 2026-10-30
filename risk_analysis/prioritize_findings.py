import json
import csv
from pathlib import Path
from collections import Counter

# Input files
GRYPE_FILE = "grype-results.json"
TRIVY_FILE = "trivy-results.json"
SBOM_FILE = "sbom.json"

# Output files
OUTPUT_DIR = Path("risk_analysis")
JSON_OUTPUT = OUTPUT_DIR / "prioritized-findings.json"
CSV_OUTPUT = OUTPUT_DIR / "prioritized-findings.csv"

SEVERITY_SCORES = {
    "CRITICAL": 100,
    "HIGH": 80,
    "MEDIUM": 50,
    "LOW": 25,
    "UNKNOWN": 0
}

WEIGHTS = {
    "severity": 0.40,
    "cvss": 0.30,
    "epss": 0.20,
    "agreement": 0.10
}


def load_json(filename):
    with open(filename, "r") as file:
        return json.load(file)


def normalize_severity(severity):
    severity = (severity or "UNKNOWN").upper()

    if severity not in SEVERITY_SCORES:
        return "UNKNOWN"

    return severity


def add_finding(findings, cve, package, version, severity,
                cvss=None, epss=None, fixed_versions=None,
                scanner=None):

    if not cve:
        return

    package = package or "unknown"
    version = version or "unknown"

    # Same CVE, package, and installed version = same finding
    key = (cve.upper(), package.lower(), version)

    if key not in findings:
        findings[key] = {
            "cve": cve.upper(),
            "package": package,
            "installed_version": version,
            "severity": "UNKNOWN",
            "cvss": None,
            "epss": None,
            "fixed_versions": set(),
            "scanners": set()
        }

    finding = findings[key]

    severity = normalize_severity(severity)

    if SEVERITY_SCORES[severity] > SEVERITY_SCORES[finding["severity"]]:
        finding["severity"] = severity

    if cvss is not None:
        finding["cvss"] = max(
            finding["cvss"] or 0,
            cvss
        )

    if epss is not None:
        finding["epss"] = max(
            finding["epss"] or 0,
            epss
        )

    for fixed in fixed_versions or []:
        if fixed:
            finding["fixed_versions"].add(str(fixed))

    if scanner:
        finding["scanners"].add(scanner)


def parse_grype(findings, data):
    for match in data.get("matches", []):
        vulnerability = match.get("vulnerability", {})
        artifact = match.get("artifact", {})
        fix = vulnerability.get("fix", {})

        cvss_scores = []

        for entry in vulnerability.get("cvss", []):
            score = entry.get("metrics", {}).get("baseScore")

            if score is not None:
                cvss_scores.append(float(score))

        epss_scores = [
            float(entry["epss"])
            for entry in vulnerability.get("epss", [])
            if entry.get("epss") is not None
        ]

        add_finding(
            findings=findings,
            cve=vulnerability.get("id"),
            package=artifact.get("name"),
            version=artifact.get("version"),
            severity=vulnerability.get("severity"),
            cvss=max(cvss_scores) if cvss_scores else None,
            epss=max(epss_scores) if epss_scores else None,
            fixed_versions=fix.get("versions", []),
            scanner="Grype"
        )


def parse_trivy(findings, data):
    for result in data.get("Results", []):
        vulnerabilities = result.get("Vulnerabilities") or []

        for vulnerability in vulnerabilities:
            cvss_scores = []

            for vendor in vulnerability.get("CVSS", {}).values():
                for key in ("V3Score", "V2Score"):
                    score = vendor.get(key)

                    if score is not None:
                        cvss_scores.append(float(score))

            fixed_version = vulnerability.get("FixedVersion")

            add_finding(
                findings=findings,
                cve=vulnerability.get("VulnerabilityID"),
                package=vulnerability.get("PkgName"),
                version=vulnerability.get("InstalledVersion"),
                severity=vulnerability.get("Severity"),
                cvss=max(cvss_scores) if cvss_scores else None,
                fixed_versions=[fixed_version] if fixed_version else [],
                scanner="Trivy"
            )


def calculate_risk(finding):
    severity_score = SEVERITY_SCORES[finding["severity"]]

    # Only use factors for which we have actual data.
    factors = {
        "severity": severity_score,
        "agreement": (
            100 if len(finding["scanners"]) > 1 else 0
        )
    }

    if finding["cvss"] is not None:
        factors["cvss"] = min(finding["cvss"] * 10, 100)

    if finding["epss"] is not None:
        factors["epss"] = min(finding["epss"] * 100, 100)

    available_weight = sum(
        WEIGHTS[factor] for factor in factors
    )

    score = sum(
        factors[factor] * WEIGHTS[factor]
        for factor in factors
    ) / available_weight

    return round(score, 2)


def load_sbom():
    data = load_json(SBOM_FILE)

    components = set()

    for component in data.get("components", []):
        name = (component.get("name") or "").lower()
        version = component.get("version") or "unknown"

        if name:
            components.add((name, version))

    return components, len(data.get("components", []))


def main():
    print("Starting vulnerability risk analysis...\n")

    findings = {}

    # Read scanner reports
    grype_data = load_json(GRYPE_FILE)
    trivy_data = load_json(TRIVY_FILE)

    parse_grype(findings, grype_data)
    parse_trivy(findings, trivy_data)

    # Load SBOM
    components, component_count = load_sbom()

    results = []

    for finding in findings.values():
        scanners = sorted(finding["scanners"])

        finding["scanners"] = scanners
        finding["fixed_versions"] = sorted(
            finding["fixed_versions"]
        )

        finding["scanner_agreement"] = len(scanners) > 1

        finding["fix_available"] = (
            True if finding["fixed_versions"] else None
        )

        finding["in_sbom"] = (
            finding["package"].lower(),
            finding["installed_version"]
        ) in components

        finding["risk_score"] = calculate_risk(finding)

        results.append(finding)

    # Highest risk first
    results.sort(
        key=lambda item: item["risk_score"],
        reverse=True
    )

   # Summary statistics
	severity_counts = Counter(
    	item["severity"] for item in results
	)

	scanner_counts = Counter()

	for finding in results:
    	for scanner in finding["scanners"]:
        	scanner_counts[scanner] += 1

	agreement_count = sum(
    	item["scanner_agreement"] for item in results
	)

	fix_available_count = sum(
    	bool(item["fixed_versions"]) for item in results
	)

	sbom_match_count = sum(
    	item["in_sbom"] for item in results
	)

	risk_scores = [
    	item["risk_score"] for item in results
	]

	summary = {
    	"grype_matches": len(grype_data.get("matches", [])),
    	"trivy_result_sections": len(trivy_data.get("Results", [])),
    	"unique_combined_findings": len(results),
    	"unique_cve_ids": len(set(item["cve"] for item in results)),
    	"detected_by_both_scanners": agreement_count,
    	"grype_findings": scanner_counts["Grype"],
    	"trivy_findings": scanner_counts["Trivy"],
    	"fix_version_reported": fix_available_count,
    	"sbom_components": component_count,
    	"findings_matched_to_sbom": sbom_match_count,
    	"severity_counts": dict(severity_counts),
    	"risk_score_minimum": min(risk_scores) if risk_scores else 0,
    	"risk_score_maximum": max(risk_scores) if risk_scores else 0,
    	"risk_score_average": round(
        	sum(risk_scores) / len(risk_scores), 2
    	) if risk_scores else 0
	}

    # Save JSON report
    report = {
        "summary": summary,
        "scoring_weights": WEIGHTS,
        "findings": results
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with open(JSON_OUTPUT, "w") as file:
        json.dump(report, file, indent=4)

    # Save CSV report
    fields = [
        "cve",
        "package",
        "installed_version",
        "severity",
        "cvss",
        "epss",
        "fixed_versions",
        "fix_available",
        "scanners",
        "scanner_agreement",
        "in_sbom",
        "risk_score"
    ]

    with open(CSV_OUTPUT, "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()

        for finding in results:
            row = finding.copy()
            row["fixed_versions"] = ", ".join(
                row["fixed_versions"]
            )
            row["scanners"] = ", ".join(row["scanners"])
            writer.writerow(row)

    # Display results
    print("Risk analysis completed!")
    print("=" * 45)
    print(f"Grype matches: {summary['grype_matches']}")
    print(f"Unique combined findings: {len(results)}")
    print(f"Detected by both scanners: {agreement_count}")
    print(f"SBOM components: {component_count}")
	print(f"Unique CVE IDs: {summary['unique_cve_ids']}")
	print(f"Grype findings: {summary['grype_findings']}")
	print(f"Trivy findings: {summary['trivy_findings']}")
	print(f"Fix versions reported: {summary['fix_version_reported']}")
	print(f"SBOM matches: {summary['findings_matched_to_sbom']}")
	print(f"Average risk score: {summary['risk_score_average']}")
    print("\nFindings by severity:")

    for severity in (
        "CRITICAL", "HIGH", "MEDIUM", "LOW", "UNKNOWN"
    ):
        print(f"{severity}: {severity_counts.get(severity, 0)}")

    print("\nTop 10 highest-risk findings:")

    for finding in results[:10]:
        print(
            f"{finding['cve']} | "
            f"{finding['package']} | "
            f"{finding['severity']} | "
            f"Risk: {finding['risk_score']} | "
            f"Scanners: {', '.join(finding['scanners'])}"
        )

    print("\nReports saved:")
    print(JSON_OUTPUT)
    print(CSV_OUTPUT)


if __name__ == "__main__":
    try:
        main()
    except FileNotFoundError as error:
        print(f"Missing input file: {error.filename}")
    except json.JSONDecodeError as error:
        print(f"Invalid JSON file: {error}")
    except Exception as error:
        print(f"Analysis failed: {error}")

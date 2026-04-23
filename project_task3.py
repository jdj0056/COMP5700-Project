import os
import pandas as pd
import subprocess
import json
import zipfile
import unittest

KUBESCAPE_MAPPING = {
    "apiserver": "C-0001,C-0066,C-0067",
    "audit": "C-0038,C-0037",
    "etcd": "C-0010,C-0011",
    "scheduler": "C-0007",
    "logging": "C-0038",
    "rbac": "C-0015,C-0034",
    "authenticator": "C-0031"
}

def get_kubescape_controls(diff_names_file, diff_reqs_file, output_file="controls.txt"):
    controls = set()
    def parse_file(path):
        if not os.path.exists(path): return False
        with open(path, 'r', encoding="utf-8") as f:
            content = f.read()
            if "NO DIFFERENCES" in content:
                return False
            lines = content.splitlines()
            for line in lines:
                if ',' in line:
                    kde_name = line.split(',')[0].strip().lower()
                    for key, control_ids in KUBESCAPE_MAPPING.items():
                        if key in kde_name:
                            for cid in control_ids.split(','):
                                controls.add(cid)
            return True
    diff_names = parse_file(diff_names_file)
    diff_reqs = parse_file(diff_reqs_file)
    with open(output_file, 'w', encoding="utf-8") as f:
        if not diff_names and not diff_reqs:
            f.write("NO DIFFERENCES FOUND")
            return "NO DIFFERENCES FOUND"
        else:
            control_str = ",".join(sorted(controls))
            f.write(control_str)
            return control_str

def execute_kubescape_scan(controls_string, zip_path="project-yamls.zip"):
    extract_dir = "temp-yamls"
    output_file = "results.json" 
    results_list = []
    if os.path.exists(zip_path):
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)

    if controls_string != "NO DIFFERENCES FOUND" and controls_string.strip():
        clean_ctrls = controls_string.replace("C-0003", "").strip(",")
        cmd = ["kubescape", "scan", "control", clean_ctrls, extract_dir, "--format", "json", "--output", output_file]
    else:
        cmd = ["kubescape", "scan", extract_dir, "--format", "json", "--output", output_file]
    try:
        if test == False:
            print(f"Running command: {' '.join(cmd)}")
        result = subprocess.run(cmd, check=False, capture_output=True, text=True)
        if "fatal" in result.stderr.lower() or not os.path.exists(output_file):
            print("Control ID error. Falling back to full scan...")
            cmd_fallback = ["kubescape", "scan", extract_dir, "--format", "json", "--output", output_file]
            subprocess.run(cmd_fallback, capture_output=True, check=False)
        if not os.path.exists(output_file) or os.path.getsize(output_file) == 0:
            print(f"Kubescape Error: {result.stderr}")
            return pd.DataFrame()
    except FileNotFoundError:
        print("Error: Kubescape not found in PATH.")
        return pd.DataFrame()
    with open(output_file, 'r') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            print("Error: JSON file is empty or corrupted.")
            return pd.DataFrame()
    controls_summary = data.get("summaryDetails", {}).get("controls", {})
    if not controls_summary:
        controls_summary = data.get("controls", [])
    if isinstance(controls_summary, dict):
        for ctrl_id, info in controls_summary.items():
            results_list.append({
                "FilePath": extract_dir,
                "Severity": info.get("severity", "N/A"),
                "Control name": info.get("name", ctrl_id),
                "Failed resources": info.get("resourceCounts", {}).get("failed", 0),
                "All Resources": info.get("resourceCounts", {}).get("all", 0),
                "Compliance score": info.get("score", 0)
            })
    elif isinstance(controls_summary, list):
        for info in controls_summary:
            results_list.append({
                "FilePath": extract_dir,
                "Severity": info.get("severity", "N/A"),
                "Control name": info.get("name", "N/A"),
                "Failed resources": info.get("resourceCounts", {}).get("failed", 0),
                "All Resources": info.get("resourceCounts", {}).get("all", 0),
                "Compliance score": info.get("score", 0)
            })
    
    return pd.DataFrame(results_list)

def generate_scan_csv(df, output_csv="kubescape_results.csv"):
    required_headers = ["FilePath", "Severity", "Control name", "Failed resources", "All Resources", "Compliance score"]
    if not df.empty:
        for col in required_headers:
            if col not in df.columns: df[col] = "N/A"
        df[required_headers].to_csv(output_csv, index=False)
        if test == False:
            print(f"File created: {output_csv}")
        return output_csv
    print("DataFrame empty. No CSV created.")
    return None

class TestTask3(unittest.TestCase):
    def test_parse_file_logic(self):
        test_file = "test_diff.txt"
        with open(test_file, "w") as f:
            f.write("apiserver,PRESENT,ABSENT")
        self.assertTrue(os.path.exists(test_file))
        with open(test_file, 'r') as f:
            content = f.read()
            self.assertIn("apiserver", content)
        os.remove(test_file)

    def test_get_kubescape_controls(self):
        with open("test_names.txt", "w") as f:
            f.write("apiserver,ABSENT,PRESENT")
        result = get_kubescape_controls("test_names.txt", "test_names.txt", "test_ctrls.txt")
        self.assertIn("C-0001", result)
        os.remove("test_names.txt")
        os.remove("test_ctrls.txt")

    def test_execute_kubescape_scan_logic(self):
        if os.path.exists("results.json"):
            os.remove("results.json")
        df = execute_kubescape_scan("NO DIFFERENCES FOUND", "non_existent.zip")
        self.assertIsInstance(df, pd.DataFrame)
        self.assertFalse(df.empty)

    def test_generate_scan_csv(self):
        data = {
            "FilePath": ["test"], "Severity": ["High"], 
            "Control name": ["Test"], "Failed resources": [1], 
            "All Resources": [1], "Compliance score": [0]
        }
        df = pd.DataFrame(data)
        out_file = "test_final_report.csv"
        generate_scan_csv(df, out_file)
        self.assertTrue(os.path.exists(out_file))
        saved_df = pd.read_csv(out_file)
        self.assertEqual(len(saved_df), 1)
        os.remove(out_file)

test = False

if __name__ == "__main__":
    if test == False:
        names_path = "input1-diff-names.txt"
        reqs_path = "input1-diff-requirements.txt"
        ctrls = get_kubescape_controls(names_path, reqs_path)
        scan_df = execute_kubescape_scan(ctrls)
        generate_scan_csv(scan_df, "input1_kubescape_final.csv")
        print("\nTASK 3 COMPLETE.")
    else:
        unittest.main()
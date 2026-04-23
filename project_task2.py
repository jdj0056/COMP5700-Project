import yaml
import os
import unittest

COMBINATIONS = [
    ("cis-r1-kdes.yaml", "cis-r2-kdes.yaml"),
]

# Comment out the other COMBINATIONS and remove the comment from this one to run all 9 combinations together
''' COMBINATIONS = [
    ("cis-r1-kdes.yaml", "cis-r1-kdes.yaml"), ("cis-r1-kdes.yaml", "cis-r2-kdes.yaml"),
    ("cis-r1-kdes.yaml", "cis-r3-kdes.yaml"), ("cis-r1-kdes.yaml", "cis-r4-kdes.yaml"),
    ("cis-r2-kdes.yaml", "cis-r2-kdes.yaml"), ("cis-r2-kdes.yaml", "cis-r3-kdes.yaml"),
    ("cis-r2-kdes.yaml", "cis-r4-kdes.yaml"), ("cis-r3-kdes.yaml", "cis-r3-kdes.yaml"),
    ("cis-r3-kdes.yaml", "cis-r4-kdes.yaml")
] '''

def load_yaml_files(file_path1, file_path2):
    def normalize(data):
        normalized = {}
        if not isinstance(data, dict):
            return normalized
        
        for key, value in data.items():
            req_set = set()
            if isinstance(value, dict) and 'requirements' in value:
                reqs = value['requirements']
                if isinstance(reqs, list):
                    req_set = set(str(r) for r in reqs if r)
                elif isinstance(reqs, str):
                    req_set = {reqs}
            elif isinstance(value, dict):
                req_set = set(f"{k}: {v}" for k, v in value.items() if k != 'name')
            elif isinstance(value, (str, list)):
                req_set = {str(value)} if isinstance(value, str) else set(str(v) for v in value)   
            normalized[key.lower().strip()] = req_set
        return normalized

    try:
        with open(file_path1, 'r', encoding="utf-8") as f1, \
             open(file_path2, 'r', encoding="utf-8") as f2:
            raw1 = yaml.safe_load(f1) or {}
            raw2 = yaml.safe_load(f2) or {}
            return normalize(raw1), normalize(raw2)
    except Exception as e:
        print(f"File loading error: {e}")
        return {}, {}

def compare_element_names(data1, data2, file1_path, file2_path, output_file="diff_names.txt"):
    f1_name = os.path.basename(file1_path)
    f2_name = os.path.basename(file2_path)
    diff_names = []
    all_keys = set(data1.keys()) | set(data2.keys())
    for key in all_keys:
        if key in data1 and key not in data2:
            diff_names.append(f"{key},ABSENT-IN-{f2_name},PRESENT-IN-{f1_name},NA")
        elif key in data2 and key not in data1:
            diff_names.append(f"{key},ABSENT-IN-{f1_name},PRESENT-IN-{f2_name},NA")

    with open(output_file, 'w', encoding="utf-8") as f:
        if not diff_names:
            f.write("NO DIFFERENCES IN REGARDS TO ELEMENT NAMES")
        else:
            for name in sorted(diff_names):
                f.write(f"{name}\n")
    return output_file

def compare_element_requirements(data1, data2, file1_path, file2_path, output_file="diff_requirements.txt"):
    f1_req = os.path.basename(file1_path)
    f2_req = os.path.basename(file2_path)
    diff_reqs = []
    all_keys = set(data1.keys()) | set(data2.keys())
    for key in all_keys:
        if key in data1 and key not in data2:
            diff_reqs.append(f"{key},ABSENT-IN-{f2_req},PRESENT-IN-{f1_req},NA")
        elif key in data2 and key not in data1:
            diff_reqs.append(f"{key},ABSENT-IN-{f1_req},PRESENT-IN-{f2_req},NA")
        else:
            reqs1 = data1[key]
            reqs2 = data2[key]
            for r in (reqs1 - reqs2):
                diff_reqs.append(f"{key},ABSENT-IN-{f2_req},PRESENT-IN-{f1_req},{r}")
            for r in (reqs2 - reqs1):
                diff_reqs.append(f"{key},ABSENT-IN-{f1_req},PRESENT-IN-{f2_req},{r}")

    with open(output_file, 'w', encoding="utf-8") as f:
        if not diff_reqs:
            f.write("NO DIFFERENCES IN REGARDS TO ELEMENT REQUIREMENTS")
        else:
            for record in sorted(diff_reqs):
                f.write(f"{record}\n")
    return output_file

class TestTask2(unittest.TestCase):
    def test_load_yaml_files(self):
        f1, f2 = "t1.yaml", "t2.yaml"
        with open(f1, "w") as a, open(f2, "w") as b:
            yaml.dump({"Apiserver": {"requirements": ["Enable"]}}, a)
            yaml.dump({"Apiserver": {"requirements": ["Disable"]}}, b)
        d1, d2 = load_yaml_files(f1, f2)
        self.assertIn("apiserver", d1)
        self.assertIn("Enable", d1["apiserver"])
        os.remove(f1)
        os.remove(f2)

    def test_compare_element_names(self):
        d1 = {"only_in_1": {"req"}}
        d2 = {"both": {"req"}}
        out = compare_element_names(d1, d2, "f1.yaml", "f2.yaml", "test_names.txt")
        with open(out, "r") as f:
            content = f.read()
            self.assertIn("only_in_1,ABSENT-IN-f2.yaml,PRESENT-IN-f1.yaml,NA", content)
        os.remove("test_names.txt")

    def test_compare_element_requirements(self):
        d1 = {"test": {"Requirement A"}}
        d2 = {"test": {"Requirement B"}}
        out = compare_element_requirements(d1, d2, "f1.yaml", "f2.yaml", "test_reqs.txt")
        with open(out, "r") as f:
            content = f.read()
            self.assertIn("test,ABSENT-IN-f1.yaml,PRESENT-IN-f2.yaml,Requirement B", content)
            
        os.remove("test_reqs.txt")

test = False

if __name__ == "__main__":
    if test == False:
        choice1 = input("\nSelect the first file number (1-4): ").strip()
        choice2 = input("Select the second file number (1-4): ").strip()
        run_number = input("Enter the run number: ").strip()
        f1 = f"cis-r{choice1}-kdes.yaml"
        f2 = f"cis-r{choice2}-kdes.yaml"
        print("/nStarting Task 2: Comparator")
        # for i, (f1, f2) in enumerate(COMBINATIONS):
        if os.path.exists(f1) and os.path.exists(f2):
            print(f"Running Input-{run_number}...")
            data1, data2 = load_yaml_files(f1, f2)
            compare_element_names(data1, data2, f1, f2, f"input{run_number}-diff-names.txt")
            compare_element_requirements(data1, data2, f1, f2, f"input{run_number}-diff-requirements.txt")
        print("\nTASK 2 COMPLETE.")
        print("Two YAML files generated for each comparison.")
    else:
        unittest.main()
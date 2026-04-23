import os
import re
import yaml
import json
import ollama
import pdfplumber
import unittest

MODEL_NAME = 'gemma3:1b'
INPUT_FILES = ["cis-r1.pdf", "cis-r2.pdf", "cis-r3.pdf", "cis-r4.pdf"]
COMBINATIONS = [
    ("cis-r1.pdf", "cis-r1.pdf"), ("cis-r1.pdf", "cis-r2.pdf"), ("cis-r1.pdf", "cis-r3.pdf"),
    ("cis-r1.pdf", "cis-r4.pdf"), ("cis-r2.pdf", "cis-r2.pdf"), ("cis-r2.pdf", "cis-r3.pdf"),
    ("cis-r2.pdf", "cis-r4.pdf"), ("cis-r3.pdf", "cis-r3.pdf"), ("cis-r3.pdf", "cis-r4.pdf"),
]

def zero_shot(text):
    base_format = '{"element_key": {"name": "Element Name", "requirements": ["req1", "req2"]}}'
    return (f"Extract security entities and requirements from this text as JSON. "
            f"Format: {base_format}\nText: {text[:1500]}")

def few_shot(text):
    base_format = '{"element_key": {"name": "Element Name", "requirements": ["req1", "req2"]}}'
    example = '{"etcd": {"name": "etcd", "requirements": ["Ensure 2700 port is closed"]}}'
    return (f"Extract security entities and requirements from this text as JSON. "
            f"Follow this example: {example} "
            f"Format: {base_format}\nText: {text[:1500]}")

def chain_of_though(text):
    base_format = '{"element_key": {"name": "Element Name", "requirements": ["req1", "req2"]}}'
    return (f"1. Identify the technical component (e.g., apiserver).\n"
            f"2. Extract specific security rules or flags for that component.\n"
            f"3. Output the result in this JSON format: {base_format}\n"
            f"Text: {text[:1500]}")

def call_gemma(text, p_type):
    if p_type == "zero-shot":
        prompt = zero_shot(text)
    elif p_type == "few-shot":
        prompt = few_shot(text)
    else:
        prompt = chain_of_though(text)
    try:
        response = ollama.generate(model=MODEL_NAME, prompt=prompt)
        raw_output = response['response']
        match = re.search(r'\{.*\}', raw_output, re.DOTALL)
        if match:
            return json.loads(match.group(0)), raw_output, prompt
    except Exception as e:
        print(f"      [!] Parsing error in {p_type}: {e}")
    return {}, "Error: No valid JSON found", prompt

def merge_kdes(master, new_data):
    if not isinstance(new_data, dict): 
        return master
        
    for key, val in new_data.items():
        norm_key = str(key).lower().replace(" ", "_").strip()
        
        if isinstance(val, list):
            val = {"name": norm_key, "requirements": val}
        elif not isinstance(val, dict):
            continue 
        if norm_key in master:
            if not isinstance(master[norm_key], dict):
                master[norm_key] = {"name": norm_key, "requirements": []}
            existing_reqs = master[norm_key].get('requirements', [])
            if not isinstance(existing_reqs, list): existing_reqs = []
            new_reqs = val.get('requirements', [])
            if not isinstance(new_reqs, list): new_reqs = []
            master[norm_key]['requirements'] = list(set(existing_reqs + new_reqs))
        else:
            master[norm_key] = val
    return master

def process_pdf(pdf_path):
    print(f"\n>>> Analyzing {pdf_path}...")
    if not os.path.exists(pdf_path):
        print(f"File {pdf_path} not found. Skipping.")
        return None, []
    full_text = ""
    with pdfplumber.open(pdf_path) as pdf:
        target_pages = pdf.pages[12:25] # Shortened to ensure the code would function
        for page in target_pages:
            full_text += page.extract_text() or ""
    chunks = [full_text[i:i+2000] for i in range(0, len(full_text), 2000)]
    master_dict = {}
    logs = []
    for p_type in ["zero-shot", "few-shot", "chain-of-thought"]:
        for chunk in chunks[:3]:
            data, raw, used_p = call_gemma(chunk, p_type)
            master_dict = merge_kdes(master_dict, data)
            logs.append({"type": p_type, "prompt": used_p, "output": raw})
    
    return master_dict, logs

class TestTask1(unittest.TestCase):
    def test_zero_shot(self):
        text = "Test input"
        result = zero_shot(text)
        self.assertIn("Extract security entities", result)
        self.assertIn(text, result)

    def test_few_shot(self):
        text = "Test input"
        result = few_shot(text)
        self.assertIn("Example:", result)
        self.assertIn("etcd", result)

    def test_chain_of_though(self):
        text = "Test input"
        result = chain_of_though(text)
        self.assertIn("1. Identify", result)
        self.assertIn("3. Output", result)

    def test_call_gemma(self):
        original_func = ollama.generate
        ollama.generate = lambda model, prompt: {'response': '{"test": {"name": "test", "requirements": []}}'}
        try:
            data, raw, prompt = call_gemma("text", "zero-shot")
            self.assertEqual(data["test"]["name"], "test")
        finally:
            ollama.generate = original_func

    def test_merge_kdes(self):
        master = {"api": {"name": "api", "requirements": ["old_req"]}}
        new_data = {"api": {"name": "api", "requirements": ["new_req"]}}
        result = merge_kdes(master, new_data)
        self.assertIn("api", result)
        self.assertTrue("new_req" in result["api"]["requirements"])
        self.assertTrue("old_req" in result["api"]["requirements"])

    def test_process_pdf_missing_file(self):
        master, logs = process_pdf("non_existent_file.pdf")
        self.assertIsNone(master)
        self.assertEqual(logs, [])

test = False

if __name__ == "__main__":
    if test == False:
        all_logs = []
        pdf_cache = {}
        comparisons = input("\nHow many extractions would you like to perform?: ").strip()
        comp = int(comparisons)
        print("Starting Task 1: Extractor")
        for i in range(comp):
            print(f"\nRunning Input-{i+1}")
            choice1 = input("\nSelect the first file number (1-4): ").strip()
            choice2 = input("Select the second file number (1-4): ").strip()
            f1 = f"cis-r{choice1}.pdf"
            f2 = f"cis-r{choice2}.pdf"
            print(f"Pair: {f1} & {f2}")
            for f in [f1, f2]:
                    kdes, logs = process_pdf(f)
                    if kdes:
                        out_name = f.replace(".pdf", "-kdes.yaml")
                        with open(out_name, 'w', encoding="utf-8") as f:
                            yaml.dump(kdes, f, allow_unicode=True)
                        pdf_cache[f] = out_name
                        all_logs.extend(logs)

        with open("llm_logs.txt", "w", encoding="utf-8") as f:
            for entry in all_logs:
                f.write(f"*LLM Name*\n{MODEL_NAME}\n*Prompt Type*\n{entry['type']}\n")
                f.write(f"*Prompt Used*\n{entry['prompt']}\n*LLM Output*\n{entry['output']}\n")
                f.write("-" * 40 + "\n")
                
        print("\n TASK 1 COMPLETE.")
        print("YAMLs and logs generated.")
    else:
        unittest.main()
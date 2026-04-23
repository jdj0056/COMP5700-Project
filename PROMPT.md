Zero-Shot:

Code: base_format = '{"element_key": {"name": "Element Name", "requirements": ["req1", "req2"]}}'
      return (f"Extract security entities and requirements from this text as JSON. "
              f"Format: {base_format}\nText: {text[:1500]}")

Plain Text: Extract security entities and requirements from this text as JSON. Format: {"element_key": {"name": "Element Name", "requirements": ["req1", "req2"]}}
            Text:

Few-Shot: 

Code: base_format = '{"element_key": {"name": "Element Name", "requirements": ["req1", "req2"]}}'
      example = '{"etcd": {"name": "etcd", "requirements": ["Ensure 2700 port is closed"]}}'
      return (f"Extract security entities and requirements from this text as JSON. "
              f"Follow this example: {example} "
              f"Format: {base_format}\nText: {text[:1500]}")

Plain Text: Extract security entities and requirements from this text as JSON. Follow this example: {"etcd": {"name": "etcd", "requirements": ["Ensure 2700 port is closed"]}} Format: {"element_key": {"name": "Element Name", "requirements": ["req1", "req2"]}
            Text:

Chain-Of-Thought: 

Code: base_format = '{"element_key": {"name": "Element Name", "requirements": ["req1", "req2"]}}'
      return (f"1. Identify the technical component (e.g., apiserver).\n"
              f"2. Extract specific security rules or flags for that component.\n"
              f"3. Output the result in this JSON format: {base_format}\n"
              f"Text: {text[:1500]}")

Plain Text: 1. Identify the technical component (e.g., apiserver).
            2. Extract specific security rules or flags for that component.
            3. Output the result in this JSON format: {"element_key": {"name": "Element Name", "requirements": ["req1", "req2"]}}
            Text: 

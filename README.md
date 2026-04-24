# COMP5700-Project

Group Members: Josh Jelich (jdj0056)

LLM Used: Gemma-3-1b

To run the project:

1. Download all 4 pdf files, the yaml.zip file, the binary file, and the 3 project_task.py files; ensure they are in the same folder (Ex. Downloads).

2. Open a terminal and navigate to the folder that these files are located in.

3. Run the binary file using: `(add command in)` (UNFINISHED)

If the binary doesn't run, or you want to run the files individually:

1. Repeat the first two steps from above.

2. Run `pip install transformers datasets evaluate accelerate torch`

3. Run `pip install ollama pdfplumber PyYAML pandas pyinstaller`

4. Run `curl -s https://raw.githubusercontent.com/kubescape/kubescape/master/install.sh | /bin/bash`

5. Run `python project_task(num).py` (Ex. running task 1 would be `python project_task1.py`).

GitHub Actions Link: https://github.com/jdj0056/COMP5700-Project/actions

All 3 tasks run automatically for all 9 combinations to be tested.

Task 1 will likely take the longest of the 3 to run, with task 2 being very quick, and task 3 being in the middle.

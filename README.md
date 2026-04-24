# COMP5700-Project

Group Members: Josh Jelich (jdj0056)

LLM Used: Gemma-3-1b

To run the project:

1. Download all of the files, or fork the repository, and ensure they are all in the same folder (Ex. Downloads).

2. Open a terminal and navigate to the folder that these files are located in using the `cd (folder)`.

3. Run the binary file using: `.\main.exe`

If the binary doesn't run for whatever reason, or you want to run the files individually:

1. Repeat the first two steps from above.

2. Run `pip install transformers datasets evaluate accelerate torch`

3. Run `pip install ollama pdfplumber PyYAML pandas pyinstaller`

4. Run `curl -s https://raw.githubusercontent.com/kubescape/kubescape/master/install.sh | /bin/bash`

5. Run `python project_task(num).py` (Ex. running task 1 would be `python project_task1.py`), or `python main.py` to run all 3 at once (You can skip steps 2-4 if you do this, as main.py will check these automatically.)

GitHub Actions Link: https://github.com/jdj0056/COMP5700-Project/actions

All 3 tasks run automatically for all 9 combinations to be tested.

Task 1 will take the longest of the 3 to run, with task 2 being very quick, and task 3 being in the middle.

* Task 1 will occasionally crash in a random spot, I believe it has something to do with Gemma rather than the code itself. Tasks 2-3 will still operate as normal if it does crash. I recommend running it again if it does crash.

If there is no way to get the code running to test it, I have uploaded a zip file of everything generated from my run of main.exe, also here is a link to the video of the run if needed: https://youtu.be/_5BcaABhupQ?si=OJR4XYmlDCg1C4go

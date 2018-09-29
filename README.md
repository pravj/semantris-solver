semantris-solver
================
> Automated solver for [Semantris](https://research.google.com/semantris/) using OpenCV and Word Embeddings

---

#### Setup
###### Clone the repository
```
git clone git@github.com:pravj/semantris-solver.git
```

###### Setup Python environment with the required packages
```
pip install -r requirements.txt
```

###### Setup OpenCV and Tesseract
- Install OpenCV and Tesseract for your OS

###### Setup word embeddings
- Download [pre-trained word2vec](https://github.com/mmihaltz/word2vec-GoogleNews-vectors) from Google News corpus
- Set the model path as an environment variable *SEMANTRIS_SOLVER_WORD2VEC_PATH*
```
export SEMANTRIS_SOLVER_WORD2VEC_PATH=/path/to/GoogleNews-vectors-negative300.bin
```

---

#### Usage
```
Semantris Solver

Usage:
  main.py play [--mode=<mode>] [--verbose]
  main.py (-h | --help)
  main.py --version

Options:
  -h --help      Show this screen
  --version      Show version
  --verbose      Print game activity logs
  --mode=<mode>  Semantris game mode [default: arcade]
```

- For now it only supports the `arcade` mode of the game.
- Using the `--verbose` flag will enable the verbose logging configuration.
```
python main.py play --mode=arcade --verbose
```
- It will take 5-10 minutes to load the word embedding model
- Start the `arcade` version (in `blue` color theme) of the game in a full screen mode
- Put the cursor in the game input field for the system to enter the suggestions
- Wait for the ~~magic~~ model to load :tada:

---

#### Arcade mode

[![Alt text](https://img.youtube.com/vi/E8QSteLOuns/0.jpg)](https://www.youtube.com/watch?v=E8QSteLOuns)

---
[Pravendra Singh](https://hackpravj.com)
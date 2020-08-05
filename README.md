# Wikimedia To Text Corpus

![Python](https://img.shields.io/badge/python-3.x-blue.svg)
![MIT license](https://img.shields.io/badge/License-MIT-green.svg)

[Wikimedia](https://www.wikimedia.org/) is the driving force behind [Wikipedia](https://www.wikipedia.org/).
They provide a monthly full backup of all the data on Wikipedia as well as their properties.
The purpose of this repo is to convert the Wikimedia dump format into our standard text corpus format.
I.E., one document per file, one sentence per line, paragraphs have a blank line between them.

# Setup

This repository follows both our standard [prerequisite](https://github.com/TextCorpusLabs/getting-started#prerequisites) and [Python](https://github.com/TextCorpusLabs/getting-started#python) instructions.

# Steps

The below document describes how to retrieve the text corpus.
The walkthrough assumes both a particular target folder and wiki.
Both of these can be modified without changing the code.
For the target folder, make sure you have a _lot_ of space.
[This page](https://dumps.wikimedia.org/backup-index.html) lists all the available wiki dumps.
In general, they are updated twice a month.
If they are still in progress, get the former dump.

1. Clone this repository then open a shell to the `~/code` directory.
2. Retrieve the dataset.
   ```{shell}
   python download_wikimedia.py -wiki enwiki -date 20200720 -dest d:/enwiki
   ```
3. Extract the data in-place.
   ```{shell}
   "C:/Program Files/7-Zip/7z.exe" e -od:/enwiki "d:/enwiki/*.bz2"
   del "d:\enwiki\*.xml.bz2"
   ```
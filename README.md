# Wikimedia To Text Corpus

![Python](https://img.shields.io/badge/python-3.x-blue.svg)
![MIT license](https://img.shields.io/badge/License-MIT-green.svg)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.3975690.svg)](https://doi.org/10.5281/zenodo.3975690)

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
**Note:** The shell syntax is PowerShell.
If you use a different shell, your syntax will be different. 

1. Clone this repository then open a PowerShell to the `~/code` directory.
2. Install the required modules (if needed).
   ```{ps1}
   pip install -r requirments.txt
   ```
3. Figure out the correct version of enwiki to download is by selecting the latest dump that is "complete".
   ```{ps1}
   $wiki = 'enwiki'
   $date = '20201101'
   ```
4. [Retrieve](./code/download_wikimedia.py) the dataset.
   ```{ps1}
   python download_wikimedia.py -wiki $wiki -date $date -dest d:/$wiki
   ```
5. Extract the data in-place.
   ```{ps1}
   . "C:/Program Files/7-Zip/7z.exe" e -od:/$wiki "d:/$wiki/*.bz2"
   del "d:\$wiki\*.xml.bz2"
   ```
5. [Convert](./code/wikimedia_to_json.py) the article text to JSONL.
   This will create a file containing all the articles in text only form.
   There is an optional parameter `-spc` that defaults to 1.
   This allows for tuning on multi core machines.
   On my PC, the best value seems to be `-spc 4`
   ```{ps1}
   python wikimedia_to_json.py -in d:/$wiki/$wiki-$date.xml -out d:/$wiki/$wiki.jsonl
   ```
6. [Tokenize](./code/tokenize_wikimedia_jsonl.py) the article text.
   This will create a file containing all the tokenized documents.
   There is an optional parameter `-spc` that defaults to 1.
   This allows for tuning on multi core machines.
   On my PC, the best value seems to be `-spc 8`
   ```{ps1}
   python tokenize_wikimedia_jsonl.py -in d:/$wiki/$wiki.jsonl -out d:/$wiki/$wiki.tokenized.jsonl
   ```

## Academic boilerplate

Below is the suggested text to add to the "Methods and Materials" section of your paper when using this _process_.
The references can be found [here](./references.bib)

> The 2020/11/01 English version of Wikipedia [@wikipedia2020] was downloaded using Wikimedia's download service [@wikimedia2020].
> The single-file data dump was then converted to a corpus of plain text articles using the process described in @wikicorpus2020.

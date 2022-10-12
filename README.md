# Wikimedia To Text Corpus

![Python](https://img.shields.io/badge/python-3.x-blue.svg)
![MIT license](https://img.shields.io/badge/License-MIT-green.svg)
![Last Updated](https://img.shields.io/badge/Last%20Updated-2022.10.12-success.svg)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.3975690.svg)](https://doi.org/10.5281/zenodo.3975690)

[Wikimedia](https://www.wikimedia.org/) is the driving force behind [Wikipedia](https://www.wikipedia.org/).
They provide a monthly full backup of all the data on Wikipedia as well as their properties.
The purpose of this repo is to convert the Wikimedia dump from the given format into the text corpus format we use.
I.E.

* The full corpus consisting of one or more JSONL(ines) files in a single folder
* One or more articles in a single JSONL(ines) file
* One article per JSON object
* Each JSON object on a single line
* Text free of markdown.

# Operation

## Install

You can install the package using the following steps:

1. `pip` install using an _admin_ prompt.
   ```{ps1}
   pip uninstall wikipedia
   pip install -v git+https://github.com/TextCorpusLabs/wikimedia.git
   python -c "import nltk;nltk.download('punkt')"
   ```

## Run

You can run the package in the following ways:

1. Download all files associated with a WikiMedia data dump.
   **NOTE**: the files are both tar'ed and gz'iped.
   You will need to extract them if you want to use the other tools.
   ```{ps1}
   wikimedia download -wiki enwiki -date 20221001 -dest d:/enwiki/dl   
   . 'C:/Program Files/7-Zip/7z.exe' x -od:/enwiki/dl d:/enwiki/dl/*.bz2 -y
   ``` 
2. Convert WikiMedia's data dump to a JSONL file containing all the articles minus any markup.
   Each JSONL file may contain more than one article.
   ```{ps1}
   wikimedia convert -source d:/enwiki/raw/enwiki-20221001.xml -dest d:/enwiki/conv
   ```
   The following are optional parameters
   * `dest_pattern` is the format of the JSON file name.
     It defaults to `wikimedia.{id:03}.jsonl`
   * `count` is the number of MXML files in a single JSON file.
     This is useful to prevent any one single file from exploding in size.
     The default is `100000`

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
6. [Tokenize](./code/tokenize_wikimedia_jsonl.py) the article text.
   This will create a file containing all the tokenized documents.
   There is an optional parameter `-spc` that defaults to 1.
   This allows for tuning on multi core machines.
   On my i7-6700k w/64GB RAM, the best value seems to be `-spc 8`
   ```{ps1}
   python tokenize_wikimedia_jsonl.py -in d:/$wiki/$wiki.jsonl -out d:/$wiki/$wiki.tokenized.jsonl
   ```

# Development

## Prerequisites

Install the required modules for each of the repositories.

1. Clone this repository then open an _Admin_ shell to the `~/` directory.
2. Install the required modules.
   ```{shell}
   pip uninstall wikimedia
   pip install -e c:/repos/TextCorpusLabs/wikimedia
   ```
3. Setup the `~/.vscode/launch.json` file (VS Code only)
   1. Click the "Run and Debug Charm"
   2. Click the "create a launch.json file" link
   3. Select "Python"
   4. Select "module" and enter _wikimedia_
   5. Select one of the following modes and add the below `args` to the launch.json file.
      The `args` node should be a sibling of the `module` node.
      They may need to be changed for your pathing.
      1. Download
         ```{json}
         "args" : [
           "download",
           "-wiki", "simplewiki",
           "-date", "20221001",
           "-dest", "d:/wikimedia/gz"]
         ```
      2. Conversion
         ```{json}
         "args" : [
           "convert",
           "-source", "d:/wikimedia/raw/simplewiki-20221001.xml",
           "-dest", "d:/wikimedia/conv"]
         ```
      3. Tokenize
         ```{json}
         "args" : [
           "tokenize",
           "-source", "d:/wikimedia/raw",
           "-dest", "d:/wikimedia/tok",
           "-dest_pattern", "{name}.tokenized.jsonl"]
         ```


# Academic boilerplate

Below is the suggested text to add to the "Methods and Materials" section of your paper when using this _process_.
The references can be found [here](./references.bib)

> The 2022/10/01 English version of Wikipedia [@wikipedia2020] was downloaded using Wikimedia's download service [@wikimedia2020].
> The single-file data dump was then converted to a corpus of plain text articles using the process described in @wikicorpus2020.

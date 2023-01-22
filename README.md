# Wikimedia To Text Corpus

![Python](https://img.shields.io/badge/python-3.x-blue.svg)
![MIT license](https://img.shields.io/badge/License-MIT-green.svg)
![Last Updated](https://img.shields.io/badge/Last%20Updated-2023.01.22-success.svg)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.3975690.svg)](https://doi.org/10.5281/zenodo.3975690)

[Wikimedia](https://www.wikimedia.org/) is the driving force behind [Wikipedia](https://www.wikipedia.org/).
They provide a monthly full backup of all the data on Wikipedia as well as their properties.
The purpose of this repo is to convert the Wikimedia dump from the given format into the text corpus format we use.
I.E.

* The full corpus consisting of one or more TXT files in a single folder
* One or more articles in a single TXT file
* Each article will have a header in the form "--- {id} ---"
* Each article will have its abstract and body extracted
* One sentence per line
* Paragraphs are separated by a blank line

# Operation

## Install

You can install the package using the following steps:

`pip` install using an _admin_ prompt.

```{ps1}
pip uninstall oas
python -OO -m pip install -v git+https://github.com/TextCorpusLabs/wikimedia.git
```

or if you have the code local

```{ps1}
pip uninstall oas
python -OO -m pip install -v c:/repos/TextCorpusLabs/wikimedia
```

## Run

You are responsible for getting the source files.
They can be found at this [site](https://dumps.wikimedia.org/backup-index.html).
You will need to further navigate into particular wiki you want to download.

You are responsible for un-compressing and validating the source files.
I recommend using [7zip](https://www.7-zip.org/).
I installed my copy using [Chocolatey](https://community.chocolatey.org/packages/7zip).

The reason you are responsible is because the dump files are a single **MASSIVE** file.
Sometimes Wikimedia will be busy and the download will be slow.
Modern browsers support resume for exactly this case.
As of 2023/01/22 it is over 90 GB in _.xml_ form.
You must make sure you have enough space before you start.

All the below commands assume the corpus is an extracted _.xml_ file.

1. Extracts the metadata from the corpus.

```{ps1}
wikimedia metadata -source d:/data/wiki/enwiki.xml -dest d:/data/wiki/enwiki.meta.csv
```

The following are required parameters:

* `source` is the _.xml_ file sourced from Wikimedia.
* `dest` is the CSV file used to store the metadata.

The following are optional parameters:

* `log` is the folder of raw XML chunks that did not process.
  It defaults to empty (not saved).

2. Convert the data to our standard format.

```{ps1}
wikimedia convert -source d:/data/wiki/enwiki.xml -dest d:/data/wiki.std
```

The following are required parameters:

* `source` is the _.xml_ file sourced from Wikimedia.
* `dest` is the folder for the converted TXT files.

The following are optional parameters:

* `lines` is the number of lines per TXT file.
  The default is 250000.
* `dest_pattern` is the format of the TXT file name.
  It defaults to `wikimedia.{id:04}.txt`.
  `id` is an increasing value that increments after `lines` are stored in a file. 
* `log` is the folder of raw XML chunks that did not process.
  It defaults to empty (not saved).

## Debug/Test

The code in this repo is setup as a module.
[Debugging](https://code.visualstudio.com/docs/python/debugging#_module) and [testing](https://code.visualstudio.com/docs/python/testing) are based on the assumption that the module is already installed.
In order to debug (F5) or run the tests (Ctrl + ; Ctrl + A), make sure to install the module as editable (see below).

```{ps1}
pip uninstall wikimedia
python -m pip install -e c:/repos/TextCorpusLabs/wikimedia
```

# Academic boilerplate

Below is the suggested text to add to the "Methods and Materials" section of your paper when using this _process_.
The references can be found [here](./references.bib)

> The 2022/10/01 English version of Wikipedia [@wikipedia2020] was downloaded using Wikimedia's download service [@wikimedia2020].
> The single-file data dump was then converted to a corpus of plain text articles using the process described in [@wikicorpus2020].

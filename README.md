# Text and Data Mining Tools

## at_search_terms_in_pdfs.py

### Authors
  * Pablo Iriarte, CHUV/IUMSP 2016 - pablo@irairte.ch
  * Jan Krause, CHUV/BiUM 2014 - jan@krause.net

### Summary
This script looks in all \*.pdf files of a directory for occurences of the terms listed in a txt file. The full text is normalized (onversion to lower case and some basic space normalisation) and the script makes a copy of files in a separate folder when one or more terms are finded (positive files). The others (negative files) are copied to another folder and corrupted files (or image pdfx without OCR) are also copied to a separate folder. The script writes also a table (CSV format with ";" separator) with the detailed results for each term  and each file provided(one line per file and one column per term).

### Notes
This script was originally created for the work "Blanc, X., Collet, T.-H., Auer, R., Fischer, R., Locatelli, I., Iriarte, P., Krause, J. Légaré, F. and Cornuz, J. (2014). Publication trends of shared decision making in 15 high impact medical journals: a full-text review with bibliometric analysis. BMC Medical Informatics and Decision Making, 14(1), 71. http://doi.org/10.1186/1472-6947-14-71

### Dependencies
Needs Python 2.7 and the following libraries:
  * pdfminer: https://pypi.python.org/pypi/pdfminer/ (documentation: http://www.unixuser.org/~euske/python/pdfminer/ )
  string
  * PyPDF2: https://pypi.python.org/pypi/PyPDF2 (documentation: https://pythonhosted.org/PyPDF2/ )
  * codecs
  * re
  * os
  * sys
  * Tkinter
  * tkFileDialog
  * time
  * shutil
  * cStringIO

### Instructions
The script could be executed from shell or directly by double click (Windows). Then 2 windows are prompted :
1. Choice of PDF folder to be scanned
2. Choice of destination forlder for the results

* The term list has to be saved in the same folder of the script and called "terms.txt" qith one term per line
* Ther's no limit to the amount of PDFs to be scanned. the time execution time is about 500 PDFs
* The positive PDFs (at least one term is found) will be copied in a new folder called "POSITIFS"
* The negative PDFs (any term was found) will be copied in a new folder called "NEGATIFS"
* The PDFs that can't be scanned for any reason (PDF image without OCR for example) will be copied in a new folder called "ILLISIBLES"
* The original PDFs are copied to a new folder called "ORIGINAUX_CRYPTES"
* The name of patient is stracted form PDF following some knowed structure and the PDF file in renamed with the 3 first letters of the patient family name
* The scripts generates a table (CSV as format and ";" as separator) with the details by term in the list. The sort order of colums is random. The fist line contains the names of each term in the list.
* Ther's a line with "_filename" and the name of each term. "_total" field contains the total number of "occurencies" for all the time . The "_ntotal" field contains the total numberm of all the terms

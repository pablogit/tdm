# Text and Data Mining Tools

## Script python to search multiple terms in multiple PDFs

### Authors
  * Pablo Iriarte, UNIGE/CHUV/IUMSP/BiUM 2014-2018, pablo@irairte.ch
  * Jan Krause, CHUV/BiUM 2014, jan@krause.net

### Summary
The script "at_search_terms_in_pdfs.py" looks in all \*.pdf files of a directory for occurences of the terms listed in a txt file. The full text is normalized (conversion to lower case and some basic blanks normalisation) and the script makes a copy of files in a separate folder when one or more terms are found (positive files). The others (negative files) are copied to another folder and corrupted files (or image pdf without OCR) are also copied to a separate folder. The script writes also a table (CSV format with ";" as separator) with the detailed results for each term  and each file provided (one line per file and one column per term). The script could also search the names of patients cited in the swiss pathology repoprts in order to change the name of file with the initials for the archival needs.

### Notes
This script was originally created for the work "Blanc, X., Collet, T.-H., Auer, R., Fischer, R., Locatelli, I., Iriarte, P., Krause, J. Légaré, F. and Cornuz, J. (2014). Publication trends of shared decision making in 15 high impact medical journals: a full-text review with bibliometric analysis. BMC Medical Informatics and Decision Making, 14(1), 71. http://doi.org/10.1186/1472-6947-14-71


### Evaluation of its use in a Tumour Registry
This program was created and evluated at the Vaud Cancer Registry (RVT, https://www.iumsp.ch/rvt) Institute for Social and Preventive Medicine, University of Lausanne, Switzerland. The results of the evaluation was presented in a poster at the 2017 GRELL annual meeting in Brussels: https://www.grell-network.org/2017-brussels

 - Title: **Evaluation of an automated tool to identify positive cases from unstructured, free-text pathology reports in a Swiss Cancer Registry**
 - Authors: Pablo Iriarte<sup>1</sup> ; Rafael Blanc Moya<sup>2</sup> ; Nadia Elia<sup>3</sup>   
<sup>1</sup> Institute for Social and Preventive Medicine, University of Lausanne, Switzerland   
<sup>2</sup> Vaud Cancer Registry, Institute for Social and Preventive Medicine, University of Lausanne, Switzerland   
<sup>3</sup> Institute of Global Health, University of Geneva, Geneva, Switzerland

 - **Abstract**: https://github.com/pablogit/tdm/blob/master/Abstract_PI_RBM_NE.pdf
 - **Poster in PDF format**: https://github.com/pablogit/tdm/blob/master/Poster_RVT_bruxelles_2017_final.pdf
 

### Dependencies
Needs Python 2.7 and the following libraries:
  * pdfminer: https://pypi.python.org/pypi/pdfminer/ (documentation: http://www.unixuser.org/~euske/python/pdfminer/ )
  * PyPDF2: https://pypi.python.org/pypi/PyPDF2 (documentation: https://pythonhosted.org/PyPDF2/ )
  * codecs
  * re
  * os
  * sys
  * Tkinter
  * tkFileDialog
  * time
  * shutil
  * string
  * cStringIO

### Instructions
The script could be executed from shell or directly by double click (Windows). Then 2 windows are prompted :
1. Choice of PDFs folder to be scanned
2. Choice of destination forlder for the results

* The term list has to be situated in the same folder of the script and called "terms.txt" with one term per line
* Ther's no limit to the amount of PDFs to be scanned. the time execution time is about 500 PDFs per minute
* The positive PDFs (at least one term is found) will be copied in a new folder called "POSITIFS"
* The negative PDFs (any term was found) will be copied in a new folder called "NEGATIFS"
* The PDFs that can't be scanned for any reason (PDF image without OCR for example) will be copied in a new folder called "ILLISIBLES"
* The original PDFs are encrypted and copied to a new folder called "ORIGINAUX_CRYPTES"
* The name of patient is stracted form PDF following some known structures in the text. The PDF is then renamed with the 3 first letters of the patient family name
* The scripts generates a table (CSV as format and ";" as separator) with the details by term in the list. The sort order of colums is random. The fist line contains the names of each term in the list.
* Ther's a line with the header "_filename" and the name of each term. The column "_total" contains the total number of "occurencies" for each term in each file. The "_ntotal" column contains the total number of different terms found in each PDF



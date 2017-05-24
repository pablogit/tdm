#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Author   : 	Pablo Iriarte, CHUV/IUMSP 2016. pablo.irairte@chuv.ch
Summary  : 	Looks in all .pdf files of a directory for occurences of the terms listed in a txt file with conversion to lower case and some basic space normalisation
Features : 	Copy of positive, negative ant corrupted files in separate folders and writes a table with the files/terms results and names extracted (CSV format with ";" separator)
Notes : 	Based in the code made by Jan Krause, CHUV/BDFM, for the work "Blanc, X., Collet, T.-H., Auer, R., Fischer, R., Locatelli, I., Iriarte, P., Krause, J. Légaré, F. and Cornuz, J. (2014).
			Publication trends of shared decision making in 15 high impact medical journals: a full-text review with bibliometric analysis. BMC Medical Informatics and Decision Making, 14(1), 71.
			http://doi.org/10.1186/1472-6947-14-71


Needs Python 2.7 pdfminer library : https://pypi.python.org/pypi/pdfminer/ (documentation sur http://www.unixuser.org/~euske/python/pdfminer/)

Instructions (French) :
Le programme peut-être lancé depuis la console ou simplement en cliquant deux fois sur le fichier.
Ensuite il y a 3 fenêtres de dialogue permettant de choisir les différents fichiers et emplacements :

1. Choisir le dossier contenant les PDFs à traiter :

2. Choisir le dossier epour l'enregistrement des résultats

	Il n'y a pas de limite dans le nombre de PDFs à traiter mais le temps d'execution est d'environ 500 PDFs par minute
	Les PDFs positifs (au moins un des termes de la liste est trouvé) sont copiés dans deux dossier créé à l'emplacement choisi avec les noms "positifs", "negatifs" et "illisibles" ajouté au nom du dossier.
	Cela écrit un tableau avec séparateur ";" et l'extension ".csv" à la fin le fichier, il peut être ouvert directement avec excel en cliquand deux fois
	L'ordre des colonnes est aléatoire. Le tableau à une colonne par terme (le nom du terme figure sur la première ligne)
	Il y a une colonne "_filename" avec les noms des fichiers, une "_total" avec le total d'occurences de tous les termes et une "_ntotal" avec le nombre de termes differents trouvés

"""

import string
import codecs
import re
import os
import sys
import Tkinter
import tkFileDialog
import time
import PyPDF2
from shutil import copyfile
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter, PDFPageAggregator
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFTextExtractionNotAllowed
from pdfminer.pdfdevice import PDFDevice
from cStringIO import StringIO
from pdfminer.pdfparser import PDFParser
from pdfminer.layout import LAParams, LTTextBox, LTTextLine, LTFigure, LTImage

# Define the master password for the PDF encryption
mypass = 'tvr16'

def with_pdf (pdf_doc, pdf_pwd, fn, *args):
	"""Open the pdf document, and apply the function, returning the results"""
	result = None
	try:
		# open the pdf file
		fp = open(pdf_doc, 'rb')
		# create a parser object associated with the file object
		parser = PDFParser(fp)
		# create a PDFDocument object that stores the document structure
		doc = PDFDocument()
		# connect the parser and document objects
		parser.set_document(doc)
		doc.set_parser(parser)
		# supply the password for initialization
		doc.initialize(pdf_pwd)
		if doc.is_extractable:
			# apply the function and return the result
			result = fn(doc, *args)
		# close the pdf file
		fp.close()
	except IOError:
		# the file doesn't exist or similar problem
		pass
	return result


def convertpdf(path, pages=None):
	result = None
	try:
		# open the pdf file
		fp = open(path, 'rb')
		# create a parser object associated with the file object
		parser = PDFParser(fp)
		# create a PDFDocument object that stores the document structure
		try:
			doc = PDFDocument(parser)
		except Exception as e:
			# print path + ' is not a readable pdf'
			return
		# connect the parser and document objects
		# parser.set_document(doc)
		# doc.set_parser(parser)
		# supply the password for initialization
		# doc.initialize(pdf_pwd)
		if doc.is_extractable:
			# apply the function and return the result
			if not pages:
				pagenums = set()
			else:
				pagenums = set(pages)
			output = StringIO()
			manager = PDFResourceManager()
			converter = TextConverter(manager, output, laparams=LAParams())
			interpreter = PDFPageInterpreter(manager, converter)
			infile = file(path, 'rb')
			for page in PDFPage.get_pages(infile, pagenums):
					interpreter.process_page(page)
			infile.close()
			converter.close()
			text = output.getvalue()
			output.close
			result = text
		else:
			# print path + ' : Warning! it could not extract text from pdf file'
			result = ''
			return
		# close the pdf file
		fp.close()
	except IOError:
		# the file doesn't exist or similar problem
		result = ''
		return
	return result


def convert_pdf_to_txt(path):
	rsrcmgr = PDFResourceManager()
	retstr = StringIO()
	codec = 'utf-8'
	laparams = LAParams()
	device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
	fp = file(path, 'rb')
	interpreter = PDFPageInterpreter(rsrcmgr, device)
	password = ""
	maxpages = 0
	caching = True
	pagenos=set()
	for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password, caching=caching, check_extractable=False):
			interpreter.process_page(page)
	fp.close()
	device.close()
	str = retstr.getvalue()
	retstr.close()
	return str

root = Tkinter.Tk()
# getting term list
# file1 = tkFileDialog.askopenfile(parent=root,mode='rb',title='Choisir la liste des termes')
# if file1 != None:
# 	terms = file1.read().splitlines()
terms_file = open('terms.txt', 'r')
terms = terms_file.read().splitlines()

# getting files to be screened
mydirin = tkFileDialog.askdirectory(parent=root,title='Choisir le dossier contenant les fichiers PDF')
os.chdir(mydirin)
fnames = os.listdir(os.getcwd())

# getting final folder
mydir = tkFileDialog.askdirectory(parent=root,title='Choisir le dossier pour l\'enregistrement des résultats')

print 'Starting folder creation'

# création des dossiers pour enregistrer les fichiers résultants
newpath_ori = mydir + '/ORIGINAUX_CRYPTES/'
newpath_pos = mydir + '/POSITIFS/'
newpath_neg = mydir + '/NEGATIFS/'
newpath_prb = mydir + '/ILLISIBLES/'
newpath_res = mydir + '/RESULTATS/'
# newpath_txt = mydir + '/text/'
if not os.path.exists(newpath_pos):
	os.makedirs(newpath_ori)
if not os.path.exists(newpath_pos):
	os.makedirs(newpath_pos)
if not os.path.exists(newpath_neg):
	os.makedirs(newpath_neg)
if not os.path.exists(newpath_prb):
	os.makedirs(newpath_prb)
if not os.path.exists(newpath_res):
	os.makedirs(newpath_res)
# if not os.path.exists(newpath_txt):
#	os.makedirs(newpath_txt)


# création des sous dossiers positifs par initials
newpath_pos_a = newpath_pos + '/A/'
newpath_pos_b = newpath_pos + '/B/'
newpath_pos_c = newpath_pos + '/C/'
newpath_pos_d = newpath_pos + '/D/'
newpath_pos_e = newpath_pos + '/E/'
newpath_pos_f = newpath_pos + '/F/'
newpath_pos_g = newpath_pos + '/G/'
newpath_pos_h = newpath_pos + '/H/'
newpath_pos_i = newpath_pos + '/I/'
newpath_pos_j = newpath_pos + '/J/'
newpath_pos_k = newpath_pos + '/K/'
newpath_pos_l = newpath_pos + '/L/'
newpath_pos_m = newpath_pos + '/M/'
newpath_pos_n = newpath_pos + '/N/'
newpath_pos_o = newpath_pos + '/O/'
newpath_pos_p = newpath_pos + '/P/'
newpath_pos_q = newpath_pos + '/Q/'
newpath_pos_r = newpath_pos + '/R/'
newpath_pos_s = newpath_pos + '/S/'
newpath_pos_t = newpath_pos + '/T/'
newpath_pos_u = newpath_pos + '/U/'
newpath_pos_v = newpath_pos + '/V/'
newpath_pos_w = newpath_pos + '/W/'
newpath_pos_x = newpath_pos + '/X/'
newpath_pos_y = newpath_pos + '/Y/'
newpath_pos_z = newpath_pos + '/Z/'

# Création d'un sous-dossier pour les fichiers sans nom
newpath_pos_na = newpath_pos + '/_NOM_INTROUVABLE/'

if not os.path.exists(newpath_pos_a):
	os.makedirs(newpath_pos_a)
if not os.path.exists(newpath_pos_b):
	os.makedirs(newpath_pos_b)
if not os.path.exists(newpath_pos_c):
	os.makedirs(newpath_pos_c)
if not os.path.exists(newpath_pos_d):
	os.makedirs(newpath_pos_d)
if not os.path.exists(newpath_pos_e):
	os.makedirs(newpath_pos_e)
if not os.path.exists(newpath_pos_f):
	os.makedirs(newpath_pos_f)
if not os.path.exists(newpath_pos_g):
	os.makedirs(newpath_pos_g)
if not os.path.exists(newpath_pos_h):
	os.makedirs(newpath_pos_h)
if not os.path.exists(newpath_pos_i):
	os.makedirs(newpath_pos_i)
if not os.path.exists(newpath_pos_j):
	os.makedirs(newpath_pos_j)
if not os.path.exists(newpath_pos_k):
	os.makedirs(newpath_pos_k)
if not os.path.exists(newpath_pos_l):
	os.makedirs(newpath_pos_l)
if not os.path.exists(newpath_pos_m):
	os.makedirs(newpath_pos_m)
if not os.path.exists(newpath_pos_n):
	os.makedirs(newpath_pos_n)
if not os.path.exists(newpath_pos_o):
	os.makedirs(newpath_pos_o)
if not os.path.exists(newpath_pos_p):
	os.makedirs(newpath_pos_p)
if not os.path.exists(newpath_pos_q):
	os.makedirs(newpath_pos_q)
if not os.path.exists(newpath_pos_r):
	os.makedirs(newpath_pos_r)
if not os.path.exists(newpath_pos_s):
	os.makedirs(newpath_pos_s)
if not os.path.exists(newpath_pos_t):
	os.makedirs(newpath_pos_t)
if not os.path.exists(newpath_pos_u):
	os.makedirs(newpath_pos_u)
if not os.path.exists(newpath_pos_v):
	os.makedirs(newpath_pos_v)
if not os.path.exists(newpath_pos_w):
	os.makedirs(newpath_pos_w)
if not os.path.exists(newpath_pos_x):
	os.makedirs(newpath_pos_x)
if not os.path.exists(newpath_pos_y):
	os.makedirs(newpath_pos_y)
if not os.path.exists(newpath_pos_z):
	os.makedirs(newpath_pos_z)
if not os.path.exists(newpath_pos_na):
	os.makedirs(newpath_pos_na)

# création des sous dossiers négatifs par initials
newpath_neg_a = newpath_neg + '/A/'
newpath_neg_b = newpath_neg + '/B/'
newpath_neg_c = newpath_neg + '/C/'
newpath_neg_d = newpath_neg + '/D/'
newpath_neg_e = newpath_neg + '/E/'
newpath_neg_f = newpath_neg + '/F/'
newpath_neg_g = newpath_neg + '/G/'
newpath_neg_h = newpath_neg + '/H/'
newpath_neg_i = newpath_neg + '/I/'
newpath_neg_j = newpath_neg + '/J/'
newpath_neg_k = newpath_neg + '/K/'
newpath_neg_l = newpath_neg + '/L/'
newpath_neg_m = newpath_neg + '/M/'
newpath_neg_n = newpath_neg + '/N/'
newpath_neg_o = newpath_neg + '/O/'
newpath_neg_p = newpath_neg + '/P/'
newpath_neg_q = newpath_neg + '/Q/'
newpath_neg_r = newpath_neg + '/R/'
newpath_neg_s = newpath_neg + '/S/'
newpath_neg_t = newpath_neg + '/T/'
newpath_neg_u = newpath_neg + '/U/'
newpath_neg_v = newpath_neg + '/V/'
newpath_neg_w = newpath_neg + '/W/'
newpath_neg_x = newpath_neg + '/X/'
newpath_neg_y = newpath_neg + '/Y/'
newpath_neg_z = newpath_neg + '/Z/'

# Création d'un sous-dossier pour les fichiers sans nom
newpath_neg_na = newpath_neg + '/_NOM_INTROUVABLE/'

if not os.path.exists(newpath_neg_a):
	os.makedirs(newpath_neg_a)
if not os.path.exists(newpath_neg_b):
	os.makedirs(newpath_neg_b)
if not os.path.exists(newpath_neg_c):
	os.makedirs(newpath_neg_c)
if not os.path.exists(newpath_neg_d):
	os.makedirs(newpath_neg_d)
if not os.path.exists(newpath_neg_e):
	os.makedirs(newpath_neg_e)
if not os.path.exists(newpath_neg_f):
	os.makedirs(newpath_neg_f)
if not os.path.exists(newpath_neg_g):
	os.makedirs(newpath_neg_g)
if not os.path.exists(newpath_neg_h):
	os.makedirs(newpath_neg_h)
if not os.path.exists(newpath_neg_i):
	os.makedirs(newpath_neg_i)
if not os.path.exists(newpath_neg_j):
	os.makedirs(newpath_neg_j)
if not os.path.exists(newpath_neg_k):
	os.makedirs(newpath_neg_k)
if not os.path.exists(newpath_neg_l):
	os.makedirs(newpath_neg_l)
if not os.path.exists(newpath_neg_m):
	os.makedirs(newpath_neg_m)
if not os.path.exists(newpath_neg_n):
	os.makedirs(newpath_neg_n)
if not os.path.exists(newpath_neg_o):
	os.makedirs(newpath_neg_o)
if not os.path.exists(newpath_neg_p):
	os.makedirs(newpath_neg_p)
if not os.path.exists(newpath_neg_q):
	os.makedirs(newpath_neg_q)
if not os.path.exists(newpath_neg_r):
	os.makedirs(newpath_neg_r)
if not os.path.exists(newpath_neg_s):
	os.makedirs(newpath_neg_s)
if not os.path.exists(newpath_neg_t):
	os.makedirs(newpath_neg_t)
if not os.path.exists(newpath_neg_u):
	os.makedirs(newpath_neg_u)
if not os.path.exists(newpath_neg_v):
	os.makedirs(newpath_neg_v)
if not os.path.exists(newpath_neg_w):
	os.makedirs(newpath_neg_w)
if not os.path.exists(newpath_neg_x):
	os.makedirs(newpath_neg_x)
if not os.path.exists(newpath_neg_y):
	os.makedirs(newpath_neg_y)
if not os.path.exists(newpath_neg_z):
	os.makedirs(newpath_neg_z)
if not os.path.exists(newpath_neg_na):
	os.makedirs(newpath_neg_na)

print 'Folder creation : done'

myfolders = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']

# Liste de prefixes pour la recherche des noms
# prefix_noms = ['nom et prenom', 'nom prenom', ' nom ', ' prenom ', ' patient ', 'madame', ' mme ', 'monsieur', ' m ', ' ne le ', ' nee le ', 'dossier n']
# prefix_results = []
# Unilabs : le nom ne figure pas et la tableau est mal reconstitué, trouver la mention "mm" ou "m" (ex. 201511_GG980.pdf)
# Genève – Cytopath : Le nom figure entre "madame " et " nee le" ou "monsieur " et " ne le" (ex. 201511_GH758.pdf)
# Cypa cytologie gynécologique : le nom vient après la mention "mm" ou "m" (ex. 201511_LG973.pdf)
# Cypa ANATOMO-PATHOLOGIQUE : Nom entre "patient " et "date de naissance" (ex. 201511_LH954.pdf)
# Aurigen : Nom entre "patient mme " et " nee le" (ex. Aurigen.pdf)
# CHUV Rapport d'autopsie : Nom entre "patient " et " [m/f] ne " (ex. Autopsie.pdf)
# CHUV Rapport cyto-pathologique :  Nom entre "patient " et " [m/f] ne " (ex. C-CHUV.pdf)
# Fribourg : parfois le nom est cité au pied de page entre "patient [0-9]+ i " et " [sb/yc] i" (ex. C1245.16_1.1_530654.pdf)
#				parfois aucune mention et le nom vient avant la data de naissance "JJ.MM.AAAA" (ex. C1146.16_1_530545.pdf)
# Argotlab : Nom entre "argotlab com " et " ne e le". Nom aussi à la fin après "patient [no de dossier] i" (ex. D4594.09_1.1_397999.pdf)
# Dermatologie CHUV : Nom entre "patient " et " [m/f] date de naissance" (ex. Dermatologie_CHUV.pdf)
# HUG : Nom entre "naissance sexe [0-9]+ " et " demande" (ex. HUG.pdf)
# IPR (Institut de pathologie romand) : Nom entre "patient " et "date de naissance" (ex. IPR.pdf)
# Meditest : Nom après "dossier n° [0-9 ]+ [m/mme]" (ex. Meditest.pdf)
# Radio-oncologie CHUV : Nom après "concerne" puis "Monsieur" ou "Madame"(ex. Radio-oncologie_CHUV.pdf)
# Synlab (idem Argotlab) : Nom entre "synlab suisse " et " [ne/nee/ne e] le". Nom aussi à la fin après "patient [no de dossier] i" (ex. D4594.09_1.1_397999.pdf)
# Viollier : Nom entre "examen histologique no" et "nom et prenom" (ex. Viollier.pdf)
# Weintraub : Nom après "patient nom prenom" (ex. Weintraub.pdf)

labos_id = {		'argotlab': 'argotlab',
					'aurigen': '2162344',
					'chuv': '021314',
					'cypa': '0213134343',
					'ipr': '0218040770',
					'meditest': '0219259580',
					'synlab': '02164161',
					'unilabs': '0228274360',
					'weintraub': 'laboratoireweintraub'}
labos_id2 = {		'cypa': 'rapportanatomopathologique',
					'unilabs': 'examenanatomopathologique'}
labos_id3 = {		'unilabs': 'examendecytologienongynecologique',
					'cypa': 'examendecytologieclinique'}
labos_pattern = {	'argotlab': ' patient [0-9]+ ([a-z\']+) ',
					'aurigen': ' (?:m|mme|mlle) ([a-z\' ]+) n[e]+ le ',
					'chuv': ' patient ([a-z\' ]+) [fm] ',
					'cypa': ' (?:m|mme|mlle) ([a-z\' ]+) [0-9 ]+',
					'cypa2': ' patient ([a-z\' ]+) date de naissance',
					'ipr': ' patient ([a-z\' ]+) date de naissance',
					'meditest': ' (?:m|mme|mlle) ([a-z\']+)',
					'synlab': ' patient [0-9]+ ([a-z\']+) ',
					'unilabs': ' (?:m|mme|mlle) ([a-z\' ]+)',
					'unilabs2': ' (?:madame|monsieur|mademoiselle|enfant) ([a-z\' ]+) n[e]+ le ',
					'weintraub': ' patient nom prenom (?:[a-z\']+) ([a-z\' ]+) demande'}

# labo par défaut (désactivé : boucle sur les labos si pas trouvé)
# labo_dafault = "chuv"
labo_dafault = ""
timestr = time.strftime("%Y%m%d-%H%M%S")
myfilesnb = len(fnames)
myfilesnb = str(myfilesnb)
myfilesnb_i = 1
print 'Searching terms and names in ' + myfilesnb + ' files : starting'

# main loop
labos = []
results = []
noms_results = []

for fname in fnames:
	print 'File ' + str(myfilesnb_i) + ' of ' + myfilesnb + ' - ' + fname + ' : starting '
	new_fname = ''.join(c for c in fname if c in string.printable)
	new_fname = new_fname.replace('.pdf', '_' + timestr + '.pdf')
	if fname.endswith('.pdf'):
		# data1 = codecs.open(fname, 'r', 'iso-8859-1').read()
		# data = data1.encode('utf-8')
		data = convertpdf(fname)
		# print data
		# data = convert_pdf_to_txt(fname)
		if data:
			data = data.lower()
			data = data.replace('&#', ' ')
			data = data.replace('\t', ' ')
			data = data.replace('\r', ' ')
			data = data.replace('\n', ' ')
			data = data.replace(',', ' ')
			data = data.replace('(', ' ')
			data = data.replace(')', ' ')
			data = data.replace('.', ' ')
			data = data.replace(';', ' ')
			data = data.replace('-', ' ')
			data = data.replace(':', ' ')
			data = data.replace('/', ' ')
			data = data.replace('  ', ' ')
			data = data.decode('utf-8').replace(u'à', 'a')
			data = data.encode('utf-8')
			data = data.decode('utf-8').replace(u'é', 'e')
			data = data.encode('utf-8')
			data = data.decode('utf-8').replace(u'è', 'e')
			data = data.encode('utf-8')
			data = data.decode('utf-8').replace(u'ë', 'e')
			data = data.encode('utf-8')
			data = data.decode('utf-8').replace(u'ô', 'o')
			data = data.encode('utf-8')
			data = data.decode('utf-8').replace(u'ö', 'o')
			data = data.encode('utf-8')
			data = data.decode('utf-8').replace(u'ï', 'i')
			data = data.encode('utf-8')
			data = data.decode('utf-8').replace(u'æ', 'ae')
			data = data.encode('utf-8')
			data = data.decode('utf-8').replace(u'œ', 'oe')
			data = data.encode('utf-8')
			data = data.replace('  ', ' ')
			data = data.replace('  ', ' ')
			data = data.replace('  ', ' ')
			data = data.replace('  ', ' ')
			data2 = data.replace(' ', '')
			result = {'_filename': new_fname}
			output = False
			total = 0
			ntotal = 0
			# Recherche des termes
			for term in terms:
				if term in data:
					result[term] = data.count(term)
					total += result[term]
					ntotal = ntotal + 1
				else:
					result[term] = 0
					total += result[term]
			# Recherche du labo
			mylabo = labo_dafault
			labosi = {'filename': new_fname}
			mypos = -1
			mypos2 = -1
			mypos3 = -1
			for labo in labos_id:
				mypos = data2.find(labos_id[labo])
				labosi[labo] = mypos
				if mypos >= 0:
					mylabo = labo
					if labo in labos_id2:
						mypos2 = data2.find(labos_id2[labo])
						if mypos2 >= 0:
							mylabo = labo + '2'
						else:
							if labo in labos_id3:
								mypos3 = data2.find(labos_id3[labo])
								if mypos3 >= 0:
									mylabo = labo + '2'
			labos.append(labosi)
			# Recherche des noms
			myname = ""
			myname2 = ""
			mypattern = ""
			myname_file = ""
			myfile = new_fname
			myname_folder = "_NOM_INTROUVABLE"
			if mylabo != "":
				mypattern = labos_pattern[mylabo]
				searchobj = re.search(mypattern, data, re.I)
				if searchobj:
					myname = searchobj.group(1)
					myname2 = myname.upper()
					myname2 = myname2.replace(' ', '_')
					myname_file = myname2[:3] + '_'
					myfile = myname_file + new_fname
					myname_folder = myname2[0]
					if myname_folder not in myfolders:
						myname_folder = "_NOM_INTROUVABLE"
			else:
				for labo in labos_pattern:
					mypattern = labos_pattern[labo]
					searchobj = re.search(mypattern, data, re.I)
					if searchobj:
						myname = searchobj.group(1)
						myname2 = myname.upper()
						myname2 = myname2.replace(' ', '_')
						myname_file = myname2[:3] + '_'
						myfile = myname_file + new_fname
						myname_folder = myname2[0]
						if myname_folder not in myfolders:
							myname_folder = "_NOM_INTROUVABLE"
						else:
							break
			noms_result = {'filename': new_fname}
			noms_result['labo'] = mylabo
			# noms_result['pattern'] = mypattern
			noms_result['name'] = myname
			noms_result['filename2'] = myfile
			noms_results.append(noms_result)
			# Ecrire le fichier convertit en txt (enlever les commentaires pour obtenir les fichiers)
			# dst = newpath_txt + '/' + new_fname + '.txt'
			# oa = open(dst, 'w')
			# oa.write(data)
			# oa.close()
			result['_total'] = total
			result['_ntotal'] = ntotal
			results.append(result)

			# Copie du fichier dans le dossier des originaux newpath_ori
			# encrypt the PDF and add a password
			dstori = newpath_ori + '/' + myfile
			pdftocrypt = PyPDF2.PdfFileReader(fname)
			writer = PyPDF2.PdfFileWriter()
			writer.appendPagesFromReader(pdftocrypt)
			writer.encrypt(mypass)
			# finally, write the encrypted PDF
			with file(dstori, "wb") as outfp:
				writer.write(outfp)
			# copyfile(fname, dst)

			# Copie du fichier dans le dossier correspondant
			if total > 0:
				dst = newpath_pos + '/' + myname_folder + '/' + myfile
				with file(dst, "wb") as outfp1:
					writer.write(outfp1)
				# copyfile(fname, dst)
			if total == 0:
				dst = newpath_neg + '/' + myname_folder + '/' + myfile
				with file(dst, "wb") as outfp2:
					writer.write(outfp2)
				# copyfile(fname, dst)
			print 'File ' + str(myfilesnb_i) + ' of ' + myfilesnb + ' - ' + fname + ' : done '
		else:
			# Remplir le tableau des termes
			result = {'_filename': new_fname}
			result['_total'] = 'NA'
			result['_ntotal'] = 'NA'
			results.append(result)
			for term in terms:
				result[term] = 'NA'
			# Remplir le tableau des labos
			noms_result = {'filename': new_fname}
			noms_result['labo'] = 'NA'
			# noms_result['pattern'] = 'NA'
			noms_result['name'] = 'NA'
			noms_result['filename2'] = new_fname
			noms_results.append(noms_result)
			# Copie du fichier dans le dossier correspondant
			dst = newpath_prb + fname
			copyfile(fname, dst)
			print 'File ' + str(myfilesnb_i) + ' of ' + myfilesnb + ' - ' + fname + ' : Warning, is not a readable pdf!'
	else:
		print 'File ' + str(myfilesnb_i) + ' of ' + myfilesnb + ' - ' + fname + ' : skip, not a .pdf file'
	myfilesnb_i = myfilesnb_i + 1


print 'Searching terms and names in ' + myfilesnb + ' files : done'
print 'Saving results for each term in a CSV file : starting'

# output to a new file
# outF = tkFileDialog.asksaveasfile(parent=root,mode='w',title='Choisir le fichier pour enregistrer les resultats en format CSV')
columns = list( results[0].keys() )
dst = newpath_res + '/results_terms_' + timestr + '.csv'
outF = open(dst, 'w')
outF.write(';'.join(columns))
outF.write('\n')
for result in results:
	out = ''
	for column in columns:
		out += str( result[column] ) + ';'
	outF.write(out)
	outF.write('\n')
outF.close()

print 'results_terms_' + timestr + '.csv : done'
print 'Saving results for names in a CSV file : starting'

# Output of names
# outF = tkFileDialog.asksaveasfile(parent=root,mode='w',title='Choisir le fichier pour enregistrer les resultats de la recherche des noms')
columns = list( noms_results[0].keys() )
dst = newpath_res + '/results_noms_' + timestr + '.csv'
outF = open(dst, 'w')
outF.write(';'.join(columns))
outF.write('\n')
for nom in noms_results:
	out = ''
	for column in columns:
		out += str( nom[column] ) + ';'
	outF.write(out)
	outF.write('\n')
outF.close()
print 'results_noms_' + timestr + '.csv : done'

# Output of labos
# columns = list( labos[0].keys() )
# dst = newpath_res + '/results_labos.csv'
# outF = open(dst, 'w')
# outF.write(';'.join(columns))
# outF.write('\n')
# for nom in labos:
# 	out = ''
# 	for column in columns:
# 		out += str( nom[column] ) + ';'
# 	outF.write(out)
# 	outF.write('\n')
# outF.close()

# output to stdout
# tentative de sorted 
# columns = sorted(list( results[0].keys() ), key=lambda results: results[0])
# columns = list( results[0].keys() )
# print('\t' + '\t'.join(columns))
# for result in results:
# 	out = ''
# 	for column in columns:
# 		out += '\t' + str( result[column] )
# 	print(out)






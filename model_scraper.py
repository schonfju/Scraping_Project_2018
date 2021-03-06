"""
Article Scraper - Scrapes pubmed for articles.  

Author: Justin Schonfeld
Date of Creation: 10-05-2018
Arguments:
An Entrez query is a required argument for this script.

Options:
--pit Check if a search term or terms is present in the title.  Search terms can be presented as a comma delimited list.  Example: (conjugation,frequency)
--pia Check if a search term or terms is present in the article.
"""

# Import libraries
import click
from Bio import Entrez
from Bio import Medline

@click.command()
@click.argument('query')
@click.option('--output',default="out",help="The name of the output file.  Should end in .tsv")
@click.option('--pit',default="???", help='Check if a search term(s) (comma delimited string) is present in the title.')
@click.option('--pia',default="???", help='Check if a search term (comma delimited string) is present in the abstract.')

def search(query,output,pit,pia):
	"""Searches PubMed using E-Utils and BioPython.

	Allows for checking for additional terms against presence in the abstract or the title."""
	click.echo('Beginning Search')
	click.echo('Query: '+query)

	# Build the output files
	main_output = output+".tsv"
	acc_output = output+"_acc.tsv"
	bio_output = output+"_bios.tsv"

	# Get the article count
	handle = Entrez.esearch(db="pubmed",term=query)
	record = Entrez.read(handle)
	article_count = record['Count']
	print("Number of articles: "+str(record['Count']))

	# Get the idlist
	# Note: Potentially inefficient - look into using history to get the results without searching a second time.
	# handle = Entrez.esearch(db="pubmed",term=query,retmax=article_count)
	print("Get the idList")
	handle = Entrez.esearch(db="pubmed",term=query,retmax=article_count)
	record = Entrez.read(handle)
	idlist = record["IdList"]

	# Get the records
	print("Get the medline records.")
	handle = Entrez.efetch(db="pubmed",id=idlist,rettype="medline")
	records = Medline.parse(handle)
	records = list(records)

	# Get the accessions related to the pubmed id
	print("Using elink to get nucleotide sequence ids from the nucleotide core from pubmed.")
	lhandle = Entrez.elink(db="nuccore",dbfrom="pubmed",id=idlist,linkname="pubmed_nucleotide_accn")
	lrecords = Entrez.read(lhandle)

	# Create the list of pubmed and sequence ids
	pidlist = []
	sidlist = []
	siddict = {}
	for record in lrecords:
		if record['LinkSetDb'] != []:
			current_id = record['IdList'][0]
			for seq_id_dict in record['LinkSetDb'][0]['Link']:
				current_seqid = seq_id_dict['Id']
				pidlist.append(current_id)
				sidlist.append(current_seqid)
				if current_id not in siddict:
					siddict[current_id] = 1
				else:
					siddict[current_id] += 1

	# #Using the list of sequence ids get the list of accessuib ids
	# print("Fetch the accessions from the nucleotide core using the sequence id list.")
	# acc_handle = Entrez.efetch(db="nuccore",id=sidlist,rettype="acc")
	# acc_list = acc_handle.read().split("\n")
	# # The last element of the list is an artifact of the splitting process so we remove it.
	# acc_list.pop()
	# spid = set(pidlist)
	# print("no. publications: %d pidlist: %d, sidlist: %d, acc_list: %d"%(len(spid),len(pidlist),len(sidlist),len(acc_list)))
	# for el in spid:
	# 	print("[%s]: %d"%(el,pidlist.count(el)))

	# with open(acc_output,"w") as outf:
	# 	outf.write("PubMed ID\tSequence ID\tGB Accession\n")
	# 	for i in range(len(pidlist)):
	# 		outf.write("%s\t%s\t%s\n"%(pidlist[i],sidlist[i],acc_list[i]))

	# Crete the list of pubmed and biosample ids
	pidlist = []
	bidlist = []
	biddict = {}
	print("Using elink to get biosample ids from the biosample database using the pubmed id list.")
	lhandle = Entrez.elink(db="biosample",dbfrom="pubmed",id=idlist)
	lrecords = Entrez.read(lhandle)

	for record in lrecords:
		if record['LinkSetDb'] != []:
			print("Ther be biosamples in them their hills!")
			current_id = record['IdList'][0]
			for bio_id_dict in record['LinkSetDb'][0]['Link']:
				current_bioid = bio_id_dict['Id']
				pidlist.append(current_id)
				bidlist.append(current_bioid)
				if current_id not in biddict:
					biddict[current_id] = 1
				else:
					biddict[current_id] += 1

	# with open(bio_output,"w") as outf:
	# 	outf.write("PubMed ID\tBioSample ID\n")
	# 	for i in range(len(pidlist)):
	# 		outf.write("%s\t%s\n"%(pidlist[i],bidlist[i]))

	# Process the list based options PIA, PIT
	pia_list = pia.split(",")
	pia_list = [term.strip() for term in pia_list]

	if pia == "???":
		num_pia_terms = 0
	else:
		num_pia_terms = len(pia_list)

	pit_list = pit.split(",")
	pit_list = [term.strip() for term in pit_list]

	if pit == "???":
		num_pit_terms = 0
	else:
		num_pit_terms = len(pit_list)

	# Write a default text file
	print("Writing main .tsv")
	with open(main_output,"w") as outf:
		# Create the header for the output tsv file
		outf.write("PubMed ID \t PubMed Central ID \t Title \t Authors \t Year of Publication \t Month of Publication \t Digital Object Identifier \t Accession Count \t Biosample Count")
		if pit != '???':
			for term in pit_list:
				outf.write(" \t "+term+"[PIT]")
		if pia != '???':
			for term in pia_list:
				outf.write(" \t "+term+"[PIA]")
		outf.write("\n")

		# Write the details of each record
		for record in records:
			# Write the PubMed ID
			pmid = record.get("PMID","?")
			outf.write(pmid)
			# Write the PubMed Central ID
			outf.write("\t")
			outf.write(record.get("PMC","?"))
			# Write the Title of the Article
			outf.write("\t")
			title = record.get("TI","?")
			outf.write(title)
			# Write the Authors List 
			# NOTE - Occassionally contains a \t
			outf.write("\t")
			outf.write(','.join(record.get("AU","?")))

			# Write the date of publication
			outf.write("\t")
			datestr = record.get("DEP","?")
			# Give priority to date of electron publication (DEP)
			if datestr == "?":
				datestr = record.get("DP","?")
				datelist = datestr.strip().split(" ")
				year = datelist[0]
				outf.write(year)
				# Write the year of publication
				outf.write("\t")
				if len(datelist) >= 2:
					month = datelist[1]
				else:
					month = " "
				outf.write(month)
			else:
				outf.write(datestr[0:4])
				outf.write("\t")
				outf.write(datestr[4:6])

			# Write the AID
			outf.write("\t")
			doi = "?"
			aid_list = record.get("AID","?")
			for term in aid_list:
				if term.find("doi") != -1:
					doi = term.split(" ")[0]
			doi = "http://doi.org//"+doi
			outf.write(doi)

			# Write the accession count
			outf.write("\t")
			if pmid in siddict:
				outf.write(str(siddict[pmid]))
			else:
				outf.write("0")


			# Write the biosample count
			outf.write("\t")
			if pmid in biddict:
				outf.write(str(biddict[pmid]))
			else:
				outf.write("0")

			# Write the present in title columns
			if pit!='???':
				for term in pit_list:
					outf.write("\t")
					if title.find(term) != -1:
						outf.write("1")
					else:
						outf.write("0")

			# Write the present in abstract columns
			if pia!='???':
				for term in pia_list:
					outf.write("\t")
					ab = record.get("AB","?")
					if ab.find(term) != -1:
						outf.write("1")
					else:
						outf.write("0")


			outf.write("\n")


# Main functionality
if __name__ == '__main__':
	"""Main space"""
	# Set up account credentials
	with open ("credentials.dat","r") as inf:
		# Expecting three lines 
		Entrez.email = inf.readline().strip()
		Entrez.apikey = inf.readline().strip()
		api_account = inf.readline().strip()


	# Print out basic information to stdout
	print("Scientific Inquiry Scraper")
	print("v 0.1")
	print("-----------")
	print("Libraries:")
	print("Biopython - Entrez")
	print("API Access Point:")
	print("Pubmed - Entrez")
	print("Credentials:")
	print("Associated E-mail: "+Entrez.email)
	print("Associated API account: "+api_account)
	print("-----------")

	search()


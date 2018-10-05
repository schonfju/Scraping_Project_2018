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
@click.option('--output',default="out.tsv",help="The name of the output file.  Should end in .tsv")
@click.option('--pit',default="???", help='Check if a search term(s) (comma delimited string) is present in the title.')
@click.option('--pia',default="???", help='Check if a search term (comma delimited string) is present in the abstract.')

def search(query,output,pit,pia):
	"""Searches PubMed using E-Utils and BioPython.

	Allows for checking for additional terms against presence in the abstract or the title."""
	click.echo('Beginning Search')
	click.echo('Query: '+query)

	# Get the article count
	handle = Entrez.esearch(db="pubmed",term=query)
	record = Entrez.read(handle)
	article_count = record['Count']
	print("Number of articles: "+str(record['Count']))

	# Get the idlist
	handle = Entrez.esearch(db="pubmed",term=query,retmax=article_count)
	record = Entrez.read(handle)
	idlist = record["IdList"]

	# Get the records
	handle = Entrez.efetch(db="pubmed",id=idlist,rettype="medline")
	records = Medline.parse(handle)
	records = list(records)

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
	with open(output,"w") as outf:
		# Create the header for the output tsv file
		outf.write("PubMed ID \t PubMed Central ID \t Title \t Authors \t Year of Publication \t Month of Publication \t Digital Object Identifier")
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
			outf.write(record.get("PMID","?"))
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


# Scraping_Project_2018
A wrapper for doing a bit of term based scraping of PubMed using Eutils and BioPython.

README
-------
Requires a credentials.dat file.  The file should have three lines and specify:

your_email

ncbi_API_key

ncbi_API_login


OPTIONS
---------
Change the output file.
--output "outputfile.csv"

Check if a term or terms is present in the abstract
--pia "term1,term2,term3"

Check if a term or terms is present in the title
--pit "term1,term2,term3"

EXAMPLE USAGE
----------------

python model_scraper.py "host range"

python model_scraper.py --output "my_papers.tsv" "e coli plasmid incF"

python model_scraper.py --output "my_papers.tsv" "esserchi coli" --pit "plasmid,incF,incAC"

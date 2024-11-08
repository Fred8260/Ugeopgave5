import urllib.request
import pandas as pd
import requests
from pathlib import Path
import os
import glob
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
import PyPDF2
import random


# Specify paths
list_pth = 'C:\\Users\\A-SPAC09\\Desktop\\Python\\Ugeopgave5\\GRI_2017_2020.xlsx'
pth = 'C:\\Users\\A-SPAC09\\Desktop\\Python\\Ugeopgave5\\downloaded_pdfs\\'
dwn_pth = 'C:\\Users\\A-SPAC09\\Desktop\\Python\\Ugeopgave5\\existing_downloads\\'

# Opret mapper til succes og fejl
success_pth = os.path.join(pth, "succes_downloads")
error_pth = os.path.join(pth, "fejl_downloads")

if not os.path.exists(success_pth):
    os.makedirs(success_pth)

if not os.path.exists(error_pth):
    os.makedirs(error_pth)

# Logningsopsætning
logging.basicConfig(filename=os.path.join(error_pth, "download_log.txt"), level=logging.INFO)

# check for files already downloaded
dwn_files = glob.glob(os.path.join(dwn_pth, "*.pdf"))
exist = [os.path.basename(f)[:-4] for f in dwn_files]

# specify the ID column name
ID = "BRnum"

# Indlæs Excel-fil
df = pd.read_excel(list_pth)
df = df[df['Pdf_URL'].notnull()]

# initialize lists to store results
downloaded = []
not_downloaded = []

def download_pdf(url, save_path):
    try:
        # Check if the URL is valid
        if not is_valid_url(url):
            logging.error(f"Invalid URL: {url}")
            return None
        
        # Download the file
        urllib.request.urlretrieve(url, save_path)
        logging.info(f"Downloaded: {url}")
        
        # If the file is not a valid PDF, move it to the error folder immediately
        if not validate_pdf(save_path):
            logging.error(f"Invalid PDF: {url}")
            move_to_error_folder(save_path)
            return None
        
        # If the PDF is valid, log it and return the path
        logging.info(f"Valid PDF: {url}")
        return save_path
        
    except Exception as e:
        logging.error(f"Error downloading {url}: {e}")
        return None

def is_valid_url(url):
    try:
        response = requests.head(url, allow_redirects=True, timeout=10)
        return response.status_code == 200
    except requests.RequestException as e:
        logging.error(f"Error reaching {url}: {e}")
        return False



def validate_pdf(file_path):
    """Check if the file has a valid PDF header and verify readability by checking metadata and random pages."""
    try:
        with open(file_path, "rb") as file:
            # Tjek om filen starter med en gyldig PDF-header
            header = file.read(5)
            if header != b"%PDF-":
                logging.error(f"Invalid PDF header for file: {file_path}")
                return False
            
            # Tjek PDF'en med PyPDF2 for at sikre, at siderne kan læses
            file.seek(0)
            reader = PyPDF2.PdfFileReader(file)
            
            # Prøv at læse metadata som en ekstra validering
            if reader.getDocumentInfo() is None:
                logging.error(f"Missing metadata in PDF file: {file_path}")
                return False

            num_pages = reader.getNumPages()
            
            # Tjek nogle tilfældige sider for at sikre, at de kan læses
            if num_pages > 1:
                random_pages = random.sample(range(num_pages), min(3, num_pages))
            else:
                random_pages = [0]  # Hvis kun én side, tjek den første side
            
            for page_num in random_pages:
                reader.getPage(page_num)
            
            return True  # Hvis ingen fejl opstod, betragtes PDF'en som valid
        
    except (PyPDF2.utils.PdfReadError, IndexError, KeyError, TypeError, ValueError) as e:
        logging.error(f"PDF validation failed for {file_path}: {e}")
        return False




def move_to_error_folder(file_path):
    """Move the corrupted PDF to the error folder"""
    corrupted_file = os.path.join(error_pth, os.path.basename(file_path))
    os.rename(file_path, corrupted_file)
    logging.info(f"Moved corrupted file to error folder: {corrupted_file}")

def download_reports(row):
    url = row['Pdf_URL'] if pd.notnull(row['Pdf_URL']) else row['AM']
    file_path = os.path.join(success_pth if row['Pdf_URL'] else error_pth, f"{row['BRnum']}.pdf")
    result = download_pdf(url, file_path)
    
    if result:
        downloaded.append(row['BRnum'])
    else:
        not_downloaded.append(row['BRnum'])

# Use ThreadPoolExecutor for multithreading
with ThreadPoolExecutor(max_workers=10) as executor:
    futures = {
        executor.submit(download_reports, row): row['BRnum']
        for index, row in df.iterrows()
    }
    
    for future in as_completed(futures):
        br_nummer = futures[future]
        try:
            future.result()
        except Exception as e:
            logging.error(f"Error processing {br_nummer}: {e}")

# Log de ikke-downloadede filer
if not_downloaded:
    with open(os.path.join(error_pth, "not_downloaded.txt"), 'w') as error_log:
        for file in not_downloaded:
            error_log.write(f"{file}\n")

# Log de succesfulde og fejlede downloads
logging.info(f"Downloaded files: {downloaded}")
logging.info(f"Files not downloaded: {not_downloaded}")

# Output result
print("Downloaded files:", downloaded)
print("Files not downloaded:", not_downloaded)
print("Download process completed.")

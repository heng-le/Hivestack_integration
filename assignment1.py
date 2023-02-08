import requests
from datetime import datetime, timezone
import argparse
import xml.etree.ElementTree as ET
import pandas as pd
import sys
import io
from contextlib import redirect_stderr

# API key 
api_key = "$2b$12$DnC/KfSo0tJ2wgddmD1ca.:899d8f1b-ebed-4a15-8c2a-23cffd913826"

parser = argparse.ArgumentParser(description='Integration between Hivestack platform and a Legacy CMS system')
parser.add_argument('units', metavar='UNIT', type=str, nargs='+', help='List of external screen IDs')
parser.add_argument('-n', '--number-of-plays-per-hour', type=int, default=10, help='Number of plays per hour (default: 10)')

try:
    stderr = io.StringIO()
    with redirect_stderr(stderr):
        # Parse the command line arguments
        args = parser.parse_args()
except SystemExit as e:
    if e.code == 2:
        print("Please make sure you have inputted screen IDs as well as an integer for number of plays.")
    sys.exit(e.code)

finally:
    stderr.close()

# Access the arguments as attributes of the args object
units = args.units #list
number_of_plays_per_hour = args.number_of_plays_per_hour #int




# Function that will return the 3 different URLs after giving the screen_id as a parameter
def get_urls(screen_id):
    url = "https://staging.hivestack.cn/nirvana/api/v1/units/schedulevast/" + screen_id
    headers = {'hs-auth': ('apikey ' + api_key), "accept": "application/xml"}
    response = requests.get(url, headers=headers)
    
    # This is the raw XML file
    xml_content = response.content

    # Decoding the XML file with utf-8
    xml_str = xml_content.decode('utf-8')

    try:
        root = ET.fromstring(xml_str)
        # Accessing elements in the XML tree
        impression_url = root.find('.//Impression').text
        error_url = root.find('.//Error').text
        media_url = root.find('.//MediaFile').text

        return impression_url, error_url, media_url
    except Exception as e:
        print("Unfortunately, your input is invalid. Please make sure that you input the correct screen ID.") 
        sys.exit(1)

        
# Create a pandas dataframe that will contain all of the information 
df = pd.DataFrame(columns = ['External_ID', 'Request_time_UTC', 'Impression_URL','Error_URL','MediaFile_URL'])

for element in units:
    for num in range(number_of_plays_per_hour):
        urls = get_urls(element)
        df = df.append({'External_ID' : element, 'Request_time_UTC' : datetime.now(timezone.utc), 'Impression_URL' : urls[0].strip(), 'Error_URL' : urls[1].strip(),
        'MediaFile_URL' : urls[2].strip()}, ignore_index = True)

df.to_csv('output.csv', index=False)


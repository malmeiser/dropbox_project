"""Program to take a csv and create folders in Dropbox.
Folder path for each applicaiton = Ireland/app/uid
TO DO: Write essay to .txt in each folder and upload photo  """

import csv
import os

import dropbox

#from apikeys import
DROPBOX_APP_KEY = 'fvfu8k112h8tnm7'
DROPBOX_APP_SECRET = 'gumzf0mdxy1jfhe'
ROOT_PATH = '/Ireland/{app}/'
FOLDER_FORMAT = '{uid}'

DROPBOX_ACCESS_TOKEN_FILE = 'jEhBRKh2ZYAAAAAAAAAAM3VcRsTsxnx41AiokFFCjTo2OZZRagz4el0x3_6weWms'


def get_dropbox_access_token():
    #Get an access token for Dropbox
    if os.path.isfile(DROPBOX_ACCESS_TOKEN_FILE):
        # there is an existing access token, return it
        with open(DROPBOX_ACCESS_TOKEN_FILE) as file:
            access_token = file.read().strip()
            return access_token
    else:
        access_token = None
        while access_token is None:
            auth_flow = dropbox.DropboxOAuth2FlowNoRedirect(
                DROPBOX_APP_KEY, DROPBOX_APP_SECRET)

            authorize_url = auth_flow.start()
            print '1. Go to: ' + authorize_url
            print '2. Click \"Allow\" (you might have to log in first).'
            print '3. Copy the authorization code.'
            auth_code = raw_input(
                'Enter the authorization code here: ').strip()

            try:
                access_token = auth_flow.finish(auth_code).access_token
                with open(DROPBOX_ACCESS_TOKEN_FILE, 'w') as file:
                    file.write(access_token)
                return access_token
            except Exception, e:
                print('Error: %s' % (e,))
                print('Please try again.')
                access_token = None

def get_csv_file_path():
    #Prompt user for a path to the csv file
    csv_path = ''
    while not csv_path:
        csv_path = raw_input('What is the path to the CSV file? ')
        if not os.path.isfile(csv_path):
            print 'Sorry, %s is not a valid file' % csv_path
            csv_path = ''
    
    return csv_path

def extract_csv_rows(csv_path):
    #Extract the rows of the file into a list of dictionaries.
    csv_data = []
    with open(csv_path) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            csv_data.append(row)

    return csv_data

def save_csv_rows(csv_path, csv_data):
    #write the list of dictionaries as CSV data to the file at the given path.
    if len(csv_data) < 1:
        # nothing to write
        return

    with open(csv_path, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_data[0].keys())

        writer.writeheader()
        for row in csv_data:
            writer.writerow(row)
        return

def create_dropbox_folder_path(row_dict):
    # See https://docs.python.org/2/library/string.html#format-string-syntax
    # for Python String formatting
    full_path = ROOT_PATH.format(app=row_dict['App']) + \
        FOLDER_FORMAT.format(
            uid=row_dict['UID'])
    return full_path

def main():

    access_token = get_dropbox_access_token()

    csv_path = get_csv_file_path()
    data_from_csv = extract_csv_rows(csv_path)

     # create the Dropbox connection only once
    dbx = dropbox.Dropbox(access_token)

    for app_dict in data_from_csv:
        folder_path = create_dropbox_folder_path(app_dict)
        dbx.files_create_folder(folder_path)
        share_link = dbx.sharing_create_shared_link(folder_path, True).url
        app_dict['Dropbox URL'] = share_link
        print 'Made folder for %s' % app_dict['UID']

    save_csv_rows(csv_path, data_from_csv)
    print 'All done!  %s updated' % csv_path

    if __name__ == '__main__':
        main()

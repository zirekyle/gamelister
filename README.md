# gamelister
Query the IGDB (Internet Game Database) API and return matching games

# Setup

There are two credentials required for this to operate: an IGDB API key and a Google service account credential file.

IGDB Api Key

1. Create an account here (you can use any app name):

    https://api.igdb.com/signup
    
2. After finishing account creation, navigate to the main dashboard at:

    https://api.igdb.com/
    
3. The API key will be on the right side, next to Key.

4. Copy that key and paste it into a file named .igdb_api_key in the same directory as gamelister.py

Google Service Account Credential

1. Navigate to the Google Developer Console API dashboard here:

    https://console.developers.google.com/apis/dashboard
    
2. Create a service account using the following instructions:

    https://developers.google.com/api-client-library/php/auth/service-accounts#overview
    
3. This will output a .json file. Save this file as .gsheet.service.json in the same folder as gamelister.py


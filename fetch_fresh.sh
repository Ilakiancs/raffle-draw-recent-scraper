#!/bin/bash
# Quick script to fetch fresh Instagram followers - WORKING METHOD

echo "Fetching fresh followers from Instagram..."

# Step 1: Fetch raw data from Instagram API
echo "Calling Instagram360 API for @ieeeras_iit..."
curl --request GET \
  --url 'https://instagram360.p.rapidapi.com/userfollowers/?username_or_id=Put_here' \
  --header 'x-rapidapi-host: instagram360.p.rapidapi.com' \
  --header 'x-rapidapi-key: 9d1ccd9d6fmshf515f96baa1683cp14eed1jsn5b6d08cc4694' \
  > ieeeras_iit_followers.json

# Check if the API call was successful
if [ $? -eq 0 ]; then
    echo "API call successful - got fresh data"
    
    # Step 2: Process the data for React app
    echo "Processing data for React app..."
    python3 process_Put_here_followers.py
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "SUCCESS! Fresh data ready!"
        echo "Now click 'Reload Latest Data' button in your React app"
        echo "Your raffle now has fresh real followers from Instagram"
    else
        echo "Error processing data"
    fi
else
    echo "Error fetching from Instagram API"
fi

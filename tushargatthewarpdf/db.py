

# Read the Excel sheet
df = pd.read_excel('user_log.xlsx')

# Group data by IP address
grouped_data = df.groupby('ipAddress')

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['user_behaviour']
collection = db['userdata']

# Iterate over groups and store data in MongoDB
for ipAddress, group in grouped_data:
    # Convert group data to a dictionary or JSON format
    data_to_insert = group.to_dict(orient='records')

    # Check if the user (IP address) already exists in the collection
    existing_user = collection.find_one({'ipAddress': ipAddress})

    if existing_user:
        # If user exists, append data to the existing document
        collection.update_one(
            {'ip_address': ipAddress},
            {'$push': {'user_behavior': {'$each': data_to_insert}}}
        )
    else:
        # If user does not exist, insert a new document
        collection.insert_one({'ip_address': ipAddress, 'user_behavior': data_to_insert})

client.close()

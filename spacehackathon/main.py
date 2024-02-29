from flask import Flask, redirect, request, jsonify, render_template, session, url_for
import pandas as pd
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "reg" 
# Load existing Excel file or create a new DataFrame if the file doesn't exist
excel_filename = 'user_log.xlsx'
try:
    df = pd.read_excel(excel_filename)
except FileNotFoundError:
    df = pd.DataFrame(columns=['Action', 'Target', 'Timestamp','x_Coordinates','y_Coordinates', 'browser', 'browserVersion', 'microtime', 'scrnwidth','scrnheigth' 'ipAddress','inputValue', 'url', 'starttime', 'endtime','ctrl','alt','shift','meta'])

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['user_behaviour']
collection = db['userdata']
adminlog = db['adminlog']

def update_excel_sheet():
    global df  # Declare df as a global variable
    excel_filename_new = 'updated_user_log.xlsx'
    
    # Load existing Excel file or create a new DataFrame if the file doesn't exist
    try:
        new_df = pd.read_excel(excel_filename_new)
    except FileNotFoundError:
        new_df = pd.DataFrame(columns=['Action', 'Target', 'Timestamp', 'x_Coordinates','y_Coordinates', 'browser', 'browserVersion', 'microtime', 'scrnwidth','scrnheight', 'ipAddress','inputValue', 'url', 'starttime', 'endtime','ctrl','alt','shift','meta'])

    # Check if there are new rows in the Excel file
    if not new_df.equals(df):
        df = pd.concat([df, new_df], ignore_index=True)
 

        # Save the DataFrame to the Excel file
        df.to_excel(excel_filename_new, index=False, sheet_name='Sheet1', engine='openpyxl')
        print("Excel sheet updated successfully")
    else:
        print("No new data to update in Excel sheet")

def save_to_mongodb(ipAddress, data_to_insert):
    global df  # Declare df as a global variable

    # Check if the user (IP address) already exists in the collection
    existing_user = collection.find_one({'ipAddress': ipAddress})

    if existing_user:
        existing_data = existing_user.get('user_behavior', [])

        # Identify unique data points by comparing with existing data
        unique_data = []
        for new_data_point in data_to_insert:
            is_unique = True
            for existing_data_point in existing_data:
                # Compare each attribute of the data point
                if all(new_data_point.get(attr) == existing_data_point.get(attr) for attr in new_data_point):
                    is_unique = False
                    break

            if is_unique:
                unique_data.append(new_data_point)

        if unique_data:
            # If there are unique data points, append to the existing document
            collection.update_one(
                {'ipAddress': ipAddress},
                {'$push': {'user_behavior': {'$each': unique_data}}}
            )
            print("MongoDB data updated successfully")
        else:
            print("No unique data to update in MongoDB")
    else:
        # If user does not exist, insert all data as it's unique by definition
        collection.insert_one({'ipAddress': ipAddress, 'user_behavior': data_to_insert})
        print("New MongoDB document created successfully")





def concat_to_excel(user_log):
    global df  # Declare df as a global variable

    # Append the new user log to the DataFrame
    df = pd.concat([df, pd.DataFrame([user_log])], ignore_index=True)

    # Save the DataFrame to the Excel file
    df.to_excel(excel_filename, index=False, sheet_name='Sheet1', engine='openpyxl')

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/map')
def map():
    return render_template('map.html')

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        admin = adminlog.find_one({"username": username})

        if admin and check_password_hash(admin["password"], password):
            session["username"] = username
            return redirect(url_for("adminpage"))  # Redirect to the index endpoint
        else:
            error = "Invalid username or password."

    return render_template("login.html", error=error)

@app.route("/adminpage")
def adminpage():
    if "username" in session:
        return render_template('adminpage.html')
    return render_template('home.html')



    # # Pass the error message to the template
    # return render_template("register.html", error_message=error)

@app.route('/api/log/recc', methods=['POST'])
def log_recc():
    data = request.json
    
    user_log_recc = {}
    Action = data.get('action')
    user_log_recc['Action'] = Action
    Target = data.get('target')
    user_log_recc['Target'] = Target
    data_role=data.get('dataRole')
    user_log_recc['data_role']=data_role
    ipAddress=data.get('ipAddress')
    user_log_recc['ipAddress']=ipAddress

    print(user_log_recc)

    return jsonify({'status': 'success'})

    



@app.route('/api/log', methods=['POST'])
def log_endpoint():
    global df  # Declare df as a global variable
    data = request.json
    
    user_log = {}

    Action = data.get('action')
    user_log['Action'] = Action
    Target = data.get('target')
    user_log['Target'] = Target
    Timestamp = data.get('timestamp')
    user_log['Timestamp'] = Timestamp
    x_Coordinates = data.get('x_coordinates')
    user_log['x_Coordinates'] =x_Coordinates
    y_Coordinates = data.get('y_coordinates')
    user_log['y_Coordinates'] =y_Coordinates
    browser = data.get('browser')
    user_log['browser'] = browser
    browserVersion = data.get('browserVersion')
    user_log['browserVersion'] = browserVersion
    microtime = data.get('microtime')
    user_log['microtime'] = microtime
    scrnwidth = data.get('scrnwidth')
    user_log['scrnwidth'] = scrnwidth
    scrnheight = data.get('scrnheight')
    user_log['scrnheight'] = scrnheight
    ipAddress = data.get('ipAddress')  # Corrected the variable name
    user_log['ipAddress'] = ipAddress
    inputValue=data.get('inputValue')
    user_log['inputValue']=inputValue,

    url = data.get('currentURL')
    starttime = data.get('starttime')
    endtime = data.get('endtime')
    user_log['starttime'] = starttime
    user_log['endtime'] = endtime
    ctrl = data.get('ctrl')
    alt = data.get('alt')
    shift = data.get('shift')
    meta = data.get('meta')
    user_log['ctrl'] = ctrl
    user_log['alt'] = alt
    user_log['shift'] = shift
    user_log['meta'] = meta
    user_log['url'] = url
    
   

    # Action = data1.get('action')
    # user_log['Action'] = Action
    # Target = data1.get('target')
    # user_log['Target'] = Target
    # Timestamp = data1.get('timestamp')
    # user_log['Timestamp'] = Timestamp
    # x_Coordinates = data1.get('x_coordinates')
    # user_log['x_Coordinates'] =x_Co
    # ordinates
    # y_Coordinates = data1.get('y_coordinates')
    # user_log['y_Coordinates'] =y_Coordinates
    # browser = data1.get('browser')
    # user_log['browser'] = browser
    # browserVersion = data1.get('browserVersion')
    # user_log['browserVersion'] = browserVersion
    # microtime = data1.get('microtime')
    # user_log['microtime'] = microtime
    # scrnwidth = data1.get('scrnwidth')
    # user_log['scrnwidth'] = scrnwidth
    # scrnheight = data1.get('scrnheight')
    # user_log['scrnheight'] = scrnheight
    # ipAddress = data1.get('ipAddress')  # Corrected the variable name
    # user_log['ipAddress'] = ipAddress
    # url = data1.get('currentURL')
    # starttime = data.get('starttime')
    # endtime = data1.get('endtime')
    # user_log['starttime'] = starttime
    # user_log['endtime'] = endtime
    # ctrl = data1.get('ctrl')
    # alt = data1.get('alt')
    # shift = data1.get('shift')
    # meta = data1.get('meta')
    # user_log['ctrl'] = ctrl
    # user_log['alt'] = alt
    # user_log['shift'] = shift
    # user_log['meta'] = meta
    # user_log['url'] = url
    

    # Separate functions for Excel concatenation and MongoDB data appending
    concat_to_excel(user_log)

    # Convert group data to a dictionary or JSON format
    data_to_insert = df.to_dict(orient='records')
    # print(data_to_insert)

    # Separate function for saving data to MongoDB
    save_to_mongodb(ipAddress, data_to_insert)
    
    update_excel_sheet()
    # Clear the DataFrame for the next request
    df = pd.DataFrame(columns=['Action', 'Target', 'Timestamp', 'x_Coordinates','y_Coordinates', 'browser', 'browserVersion', 'microtime', 'scrnwidth','scrnheight', 'ipAddress','inputValue', 'url', 'starttime', 'endtime','ctrl','alt','shift','meta'])

    return jsonify({'status': 'success'})


@app.route('/api/log/end', methods=['POST'])
def log_end():
    global df  # Declare df as a global variable
    data = request.json
    
    user_end_log = {}

    Action = data.get('action')
    user_end_log['Action'] = Action
    Target = data.get('target')
    user_end_log['Target'] = Target
    Timestamp = data.get('timestamp')
    user_end_log['Timestamp'] = Timestamp
    x_Coordinates = data.get('x_coordinates')
    user_end_log['x_Coordinates'] =x_Coordinates
    y_Coordinates = data.get('y_coordinates')
    user_end_log['y_Coordinates'] =y_Coordinates
    browser = data.get('browser')
    user_end_log['browser'] = browser
    browserVersion = data.get('browserVersion')
    user_end_log['browserVersion'] = browserVersion
    microtime = data.get('microtime')
    user_end_log['microtime'] = microtime
    scrnwidth = data.get('scrnwidth')
    user_end_log['scrnwidth'] = scrnwidth
    scrnheight = data.get('scrnheight')
    user_end_log['scrnheight'] = scrnheight
    ipAddress = data.get('ipAddress')  # Corrected the variable name
    user_end_log['ipAddress'] = ipAddress
    url = data.get('currentURL')
    starttime = data.get('starttime')
    endtime = data.get('endtime')
    user_end_log['starttime'] = starttime
    user_end_log['endtime'] = endtime
    # print(endtime)
    ctrl = data.get('ctrl')
    alt = data.get('alt')
    shift = data.get('shift')
    meta = data.get('meta')
    user_end_log['ctrl'] = ctrl
    user_end_log['alt'] = alt
    user_end_log['shift'] = shift
    user_end_log['meta'] = meta
    user_end_log['url'] = url

    concat_to_excel(user_end_log)
    # Convert group data to a dictionary or JSON format
    data_to_insert1 = df.to_dict(orient='records')
    # print(data_to_insert1)

    # Separate function for saving data to MongoDB
    save_to_mongodb('unknown', data_to_insert1)
    
    update_excel_sheet()
    # Clear the DataFrame for the next request
    df = pd.DataFrame(columns=['Action', 'Target', 'Timestamp', 'x_Coordinates','y_Coordinates', 'browser', 'browserVersion', 'microtime', 'scrnwidth','scrnheight', 'ipAddress','inputValue', 'url', 'starttime', 'endtime','ctrl','alt','shift','meta'])

    return jsonify({'status': 'success'})


if __name__ == '__main__':
    app.run(debug=True, port=5001)

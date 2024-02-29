from flask import Flask, redirect, request, jsonify, render_template, session, url_for
import pandas as pd
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from sklearn.preprocessing import StandardScaler
from datetime import datetime
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import plotly.express as px
import joblib

app = Flask(__name__)
app.secret_key = "reg" 
# Load existing Excel file or create a new DataFrame if the file doesn't exist
excel_filename = 'user_log.csv'
try:
    df = pd.read_csv(excel_filename)
except FileNotFoundError:
    df = pd.DataFrame(columns=['Action', 'Target', 'Timestamp','x_Coordinates','y_Coordinates', 'browser', 'browserVersion', 'microtime', 'scrnwidth','scrnheigth' 'ipAddress','inputValue', 'url', 'starttime', 'endtime','ctrl','alt','shift','meta'])

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['user_behaviour']
collection = db['userdata']
collection1 = db['ipadd']
adminlog = db['adminlog']

def update_csv_file():
    global df  # Declare df as a global variable
    csv_filename_new = 'updated_user_log.csv'

    # Load existing CSV file or create a new DataFrame if the file doesn't exist
    try:
        new_df = pd.read_csv(csv_filename_new)
    except FileNotFoundError:
        new_df = pd.DataFrame(columns=['Action', 'Target', 'Timestamp', 'x_Coordinates', 'y_Coordinates', 'browser', 'browserVersion', 'microtime', 'scrnwidth', 'scrnheight', 'ipAddress', 'inputValue', 'url', 'starttime', 'endtime', 'ctrl', 'alt', 'shift', 'meta'])

    # Check if there are new rows in the CSV file
    if not new_df.equals(df):
        df = pd.concat([df, new_df], ignore_index=True)

        # Save the DataFrame to the CSV file
        df.to_csv(csv_filename_new, index=False)
        print("CSV file updated successfully")
    else:
        print("No new data to update in CSV file")

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





def concat_to_csv(user_log):
    global df  # Declare df as a global variable

    # Append the new user log to the DataFrame
    df = pd.concat([df, pd.DataFrame([user_log])], ignore_index=True)

    # Save the DataFrame to the CSV file
    df.to_csv(excel_filename, index=False)

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
    user_log['X'] =x_Coordinates
    y_Coordinates = data.get('y_coordinates')
    user_log['Y'] =y_Coordinates
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
    concat_to_csv(user_log)

    # Convert group data to a dictionary or JSON format
    data_to_insert = df.to_dict(orient='records')
    # print(data_to_insert)

    # Separate function for saving data to MongoDB
    save_to_mongodb(ipAddress, data_to_insert)
    
    update_csv_file()
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

    concat_to_csv(user_end_log)
    # Convert group data to a dictionary or JSON format
    data_to_insert1 = df.to_dict(orient='records')
    # print(data_to_insert1)

    # Separate function for saving data to MongoDB
    save_to_mongodb('unknown', data_to_insert1)
    
    update_csv_file()
    # Clear the DataFrame for the next request
    df = pd.DataFrame(columns=['Action', 'Target', 'Timestamp', 'x_Coordinates','y_Coordinates', 'browser', 'browserVersion', 'microtime', 'scrnwidth','scrnheight', 'ipAddress','inputValue', 'url', 'starttime', 'endtime','ctrl','alt','shift','meta'])

    return jsonify({'status': 'success'})

@app.route('/admin')
def admin():
    loaded_model = joblib.load('isolation_forest_model.joblib')
    new_data = pd.read_csv('updated_user_log.csv')


    new_data[['date_numeric', 'time_numeric']] = new_data.apply(convert_timestamp, axis=1, result_type='expand')

    new_labels = ['x_Coordinates', 'y_Coordinates', 'scrnwidth', 'scrnheight']




    # Corresponding old labels
    old_labels = ['X', 'Y', 'width', 'Height']

    # Mapping new labels to old labels in the DataFrame
    for new_label, old_label in zip(new_labels, old_labels):
        new_data[old_label] = new_data[new_label]


    features = ['X', 'Y', 'width', 'Height', 'date_numeric', 'time_numeric']
    new_data_subset = new_data[features]


    new_data_subset = new_data_subset.fillna(0)


    scaler = StandardScaler()
    new_data_scaled = scaler.fit_transform(new_data_subset)


    predictions = loaded_model.predict(new_data_scaled)


    new_data['is_anomaly'] = predictions


    anomalies_in_new_data = new_data[new_data['is_anomaly'] == -1]
    #normal_data_summary = new_data[new_data['is_anomaly'] == 1][features].describe().to_html(classes='table table-striped')
    #anomalous_data_summary = new_data[new_data['is_anomaly'] == -1][features].describe().to_html(classes='table table-striped')



    anomalies_data = anomalies_in_new_data.to_html(classes='table table-striped')
    normal_data_summary = new_data[new_data['is_anomaly'] == 1][features].describe()

    # Statistical summary for anomalous data
    anomalous_data_summary = new_data[new_data['is_anomaly'] == -1][features].describe()

    plt.figure(figsize=(10, 6))
    normal_data_summary.loc['mean'].plot(kind='bar', color='blue', label='Normal Data')
    anomalous_data_summary.loc['mean'].plot(kind='bar', color='red', label='Anomalous Data')
    plt.title('Mean Values of Features')
    plt.xlabel('Features')
    plt.ylabel('Mean Value')
    plt.legend()
    plt.tight_layout()

    funnel_data = create_funnel_data(new_data)

    count_anomalies_over_time = new_data.groupby('date_numeric')['is_anomaly'].sum()
    scatter_plot_data = new_data[['X','Y', 'is_anomaly']]
    feature_distribution_data = new_data[['X', 'Y', 'width','Height', 'is_anomaly']]

    # Count of Anomalies Over Time (Line Chart)
    count_anomalies_fig = px.line(count_anomalies_over_time, x=count_anomalies_over_time.index, y='is_anomaly',
                                  labels={'is_anomaly': 'Count of Anomalies'},
                                  title='Count of Anomalies Over Time')
    count_anomalies_plot_url = plot_to_base64(count_anomalies_fig)

    # Scatter Plot of Features
    scatter_plot_fig = px.scatter(scatter_plot_data, x='X', y='Y', color='is_anomaly',
                                  labels={'is_anomaly': 'Anomaly'},
                                  title='Scatter Plot of Features')
    scatter_plot_url = plot_to_base64(scatter_plot_fig)

    # Box Plots for Feature Distribution
    feature_distribution_fig = px.box(feature_distribution_data, x='is_anomaly', y=['X', 'Y', 'width', 'Height'],
                                      labels={'is_anomaly': 'Anomaly'},
                                      title='Feature Distribution for Normal and Anomalous Data')
    feature_distribution_plot_url = plot_to_base64(feature_distribution_fig)

    # Save the plot to a BytesIO object
    img = BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)

    # Convert the BytesIO object to base64 for embedding in HTML
    plot_url = base64.b64encode(img.getvalue()).decode()

    anomaly_pattern_fig = px.line(new_data, x='date_numeric', y='is_anomaly', labels={'is_anomaly': 'Anomaly'},
                                  title='Anomaly Pattern Over Time')
    anomaly_pattern_plot_url = plot_to_base64(anomaly_pattern_fig)

    anomaly_pattern_fig1 = px.line(new_data, x='time_numeric', y='is_anomaly', labels={'is_anomaly': 'Anomaly'},
                                  title='Anomaly Pattern Over Time')
    anomaly_pattern_plot_url1 = plot_to_base64(anomaly_pattern_fig1)

    plt.close()

    return render_template('admin.html',
                           anomalies_data=anomalies_data,
                           normal_data_summary=normal_data_summary.to_html(classes='table table-striped'),
                           anomalous_data_summary=anomalous_data_summary.to_html(classes='table table-striped'),
                           count_anomalies_plot_url=count_anomalies_plot_url,
                           scatter_plot_url=scatter_plot_url,
                           feature_distribution_plot_url=feature_distribution_plot_url,
                           funnel_data=funnel_data,
                           anomaly_pattern_plot_url=anomaly_pattern_plot_url,
                           anomaly_pattern_plot_url1=anomaly_pattern_plot_url1
                           )

def convert_timestamp(row):
    timestamp_str = row['Timestamp']
    datetime_obj = datetime.fromisoformat(timestamp_str.rstrip('Z'))
    date_numeric = datetime_obj.date().toordinal()
    time_numeric = (
        datetime_obj.time().hour * 3600 +
        datetime_obj.time().minute * 60 +
        datetime_obj.time().second +
        datetime_obj.time().microsecond / 1e6
    )
    return date_numeric, time_numeric

def plot_to_base64(fig):
    img = BytesIO()
    fig.write_image(img, format='png')
    img.seek(0)
    return base64.b64encode(img.getvalue()).decode()

def create_funnel_data(data):
    # Assuming 'Action' column represents different stages in the conversion funnel
    funnel_data = pd.DataFrame(data={
        'mousemove': data[data['Action'] == 'mousemove'].shape[0],
        'click': data[data['Action'] == 'click'].shape[0],
        'zoom': data[data['Action'] == 'zoom'].shape[0],
        'scroll': data[data['Action'] == 'scroll'].shape[0],
    }, index=[0])

    return funnel_data

if __name__ == '__main__':
    app.run(debug=True, port=5000)

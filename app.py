from flask import Flask, request, jsonify, make_response, send_file
from functools import wraps
from pymongo import MongoClient
from bson import ObjectId
import random
import jwt
from twilio.rest import Client
import pandas as pd
from flask_mail import Mail, Message
from uuid import uuid4
from werkzeug.utils import secure_filename
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # , resources={r"/api/*": {"origins": "http://localhost:3000"}}

app.config['ACCOUNT_SID'] = 'AC5f88040e6854cb8c340f77e38e03970d',
app.config['ACCESS_KEY'] = 'f539a994081b7ca5e327827c48bf1b15',
app.config['TWILIO_PHONE_NUMBER'] = "+12565888672"

message_service = Client(
    'AC5f88040e6854cb8c340f77e38e03970d', 'f539a994081b7ca5e327827c48bf1b15')

client = MongoClient("mongodb://localhost:27017")
db = client['API']
signup_data = db['signup']
locat = db['locat']
histry_collection = db['histry']
type_bar_collection = db['type_bar']
feedback_collection = db['feedback_collection']
admin_login_collection = db['admin_login']
lat_long_collection = db['lat_long']
################### mail #############################################################################
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'shobhit.pal@fourbrick.com'
app.config['MAIL_PASSWORD'] = 'qdve zeva rvuc iecp'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
mail = Mail(app)
######################### stop mail ################################################################


######################## tokenization #######################################################################
def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):

        token = None
        if "Authorization" in request.headers:
            token = request.headers["Authorization"].split(" ")[-1]
            # print(token,"dasgfhgfsahgdfsahgd")

        if not token:
            return jsonify({"message": " valid token is missing", 'status': 400})

        try:
            data = jwt.decode(
                token,
                algorithms="HS512",
                key="GameDev",
            )
            # print("dsifhsdkuhfkusdhfkuhsd", data)

            aggr = [
                {
                    '$match': {
                        '_id': ObjectId(data['userId'])
                    }
                }, {
                    '$addFields': {
                        '_id': {
                            '$toString': '$_id'
                        }
                    }
                }
            ]

            current_user = list(signup_data.aggregate(aggr))

            database_data = len(current_user)

            if database_data == 0:
                return jsonify({"message": "no data", 'status': 400})

        except Exception as e:
            return jsonify({"message": "Token is invalid", 'status': 400})
        return f(current_user[0], *args, **kwargs)

    return decorator
############################# stop tokenization ##########################################

# ####################### signup page ####################################################
# @app.route("/signup", methods=['POST'])
# def signup():
#     if request.method == "POST":
#         email = request.form.get("email")
#         username = request.form.get('username')
#         password = request.form.get("password")
#         verify_password = request.form.get("verify_password")
#         receive_update_email = request.form.get("receive_update_email")
#         if password == verify_password:
#             email_exist = signup_data.find_one({"email":email} or {'username':username })
#         # phone_exist = signup_data.find_one({"mobile":mobile})

#             if email_exist:
#                 return jsonify({"message":"Email or username is already exist",'status':400})
#             # if phone_exist:
#             #     return jsonify({"message":"Phone no. is already exist",'status':400})
#             otp = random.randint(1000, 9999)
#             try:
#                 msg = Message("OTP for Registration", sender='shohit.pal@fourbrick.com', recipients=[email])
#                 msg.body = f"Your OTP for registration is: {otp}"
#                 mail.send(msg)
#                 print(otp,'otp')

#             except Exception as e:
#                 print(e)
#                 return jsonify({"message": "Error sending OTP.",'status':400}), 500
#             data = {
#                 "username":username,
#                 "email":email,
#                 "password":password,
#                 'verify_password':verify_password,
#                 "receive_update_email": receive_update_email == 'on',
#                 "verified":False,
#                 "OTP": otp,
#             }
#             signup_data.insert_one(data)
#             return jsonify({"message": "Registration successful. Please check your email for OTP.",'status':200})
#         else:
#             return jsonify('password not matched')
# ############################## stop #####################################################################################


# ####################### verify otp #########################################################################################
# @app.route("/verify", methods=['POST','GET'])
# def verify():
#     if request.method=='POST':
#         email=request.form.get('email')
#         input_otp=request.form.get('input_otp')
#         user_data = signup_data.find_one({"email": email})
#         print(user_data,'user_data')
#         stored_otp = user_data.get("OTP") if user_data else None
#         print(stored_otp)
#         if email and stored_otp:
#             if stored_otp is not None and input_otp == str(stored_otp):

#                 user_data = signup_data.update_one({"email": email}, {"$set": {"verified": True}})
#                 return jsonify({"message": "OTP verification successful.",'status':200})
#             else:
#                 return jsonify({"message": "Invalid OTP.",'status':400})
#         else:
#             return jsonify({
#                 'message':'Email or OTP is invalid','status':400
#             })
#     else:
#         return jsonify({
#             'message':'Invalid request'
#         })
# ################################################################################################################################################


@app.route("/signup", methods=['POST'])
def signup():
    if request.method == "POST":
        email = request.form.get("email")
        # username = request.form.get('username')
        # password = request.form.get("password")
        # verify_password = request.form.get("verify_password")
        # receive_update_email = request.form.get("receive_update_email")
        # if password == verify_password:
        email_exist = signup_data.find_one({"email": email})
        # phone_exist = signup_data.find_one({"mobile":mobile})

        if email_exist:
            return jsonify({"message": "Email is already exist", 'status': 400})
        # if phone_exist:
        #     return jsonify({"message":"Phone no. is already exist",'status':400})
        otp = random.randint(1000, 9999)
        try:
            msg = Message("OTP for Registration",
                          sender='shohit.pal@fourbrick.com', recipients=[email])
            msg.body = f"Your OTP for registration is: {otp}"
            mail.send(msg)
            print(otp, 'otp')
            custom_id = ObjectId()

            # Insert data with the same _id
            data = {
                "_id": custom_id,
                "email": email,
                "OTP": otp,
                "verified": False,
            }
            signup_data.insert_one(data)
            return jsonify({'message': 'otp send successfully', 'status': 200})

        except Exception as e:
            print(e)
            return jsonify({"message": "Error sending OTP.", 'status': 400}), 500

####################### verify otp #########################################################################################


@app.route("/verify", methods=['POST'])
def verify():
    if request.method == 'POST':
        email = request.form.get('email')
        print(email, 'email')
        input_otp = request.form.get('input_otp')
        print(input_otp, 'input_otp')
        user_data = signup_data.find_one({"email": email})
        print(user_data, 'user_data')
        stored_otp = user_data.get("OTP") if user_data else None
        print(stored_otp)

        if email and stored_otp:
            if stored_otp is not None and input_otp == str(stored_otp):
                # Use the same _id for the verify operation
                custom_id = user_data.get("_id")
                print(custom_id, 'custom_id')
                # Update the document with the same _id
                data = {
                    "username": request.form.get('username'),
                    "email": email,
                    'input_otp': input_otp,
                    "password": request.form.get("password"),
                    "verify_password": request.form.get("verify_password"),
                    "receive_update_email": request.form.get("receive_update_email") == 'on',
                    "verified": True,
                }
                print(data, 'dddd')
                print(signup_data.update_one(
                    {"_id": custom_id}, {"$set": data}), 'kkjjj')

                return jsonify({"message": "OTP verification successful.", 'status': 200})
            else:
                return jsonify({"message": "Invalid OTP.", 'status': 400})
        else:
            return jsonify({
                'message': 'Email or OTP is invalid', 'status': 400
            })
    else:
        return jsonify({
            'message': 'Invalid request', 'status': 400
        })


###############################################################################################################################
#################### login ################################################################################################################
@app.route("/login", methods=['POST'])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user_data = signup_data.find_one(
            {"email": email, 'password': password})
        print(user_data)
        if user_data:
            if user_data['verified']:

                if str(user_data['password']) == str(password):
                    user_data['_id'] = str(user_data['_id'])
                    del user_data['password']
                    access_token = jwt.encode(
                        {
                            "userDetails": user_data, "userId": user_data["_id"]
                        },
                        key="GameDev",
                        algorithm="HS512",
                    )
                    response = make_response(
                        jsonify({"token": access_token, "user": user_data})
                    )
                    response.set_cookie(
                        "token",
                        access_token,
                        # secure=True,
                        httponly=True,
                        samesite=None,

                    )
                    data = jwt.decode(
                        access_token,
                        algorithms="HS512",
                        key="GameDev",
                    )
                    return jsonify({"message": "Login successful.", "token": access_token, "token_Data": data, 'status': 200})

            else:
                return jsonify({"message": "User Not Verified.", 'status': 400})
        else:
            return jsonify({"message": "Email or Password wrong...", 'status': 400})

    else:
        return jsonify({"message": "Email not found. Please register first.", 'status': 400})


################## location ##########################################################
@app.route('/active_map', methods=['POST'])
@token_required
def add_location(current_user):
    # data = request.get_json()
    data = request.form.to_dict()

    if 'latitude' not in data or 'longitude' not in data:
        return jsonify({'error': 'Latitude and longitude are required'}), 400

    location = {
        'latitude': data['latitude'],
        'longitude': data['longitude'],
        'network_type': data['network_type'],
        'date': data['date']
    }

    print(location)

    result = locat.insert_one(location)
    return jsonify({'id': str(result.inserted_id)}), 201


@app.route('/find_active_map', methods=['GET'])
# @token_required
def get_all_locations():
    locations = list(locat.find({}, {'_id': 0}))
    print(locations)
    for location in locations:
        if 'latitude' in location and 'longitude' in location:
            location['latitude'] = float(location['latitude'])
            location['longitude'] = float(location['longitude'])

    return jsonify(locations)
##################### histry ########################################################


@app.route('/histry', methods=['POST'])
@token_required
def histry(current_user):
    if request.method == 'POST':
        date = request.form.get('date')
        score = request.form.get('score')
        type = request.form.get('type')
        data = {
            'date': date,
            'score': score,
            'type': type
        }
        # print(data,'kkkkkkkkkkkkkkkkkkkkkkkkk')
        result = histry_collection.insert_one(data)
        print(result)
        return jsonify({
            'message': 'histry is sccussful submited', 'status': 200
        })
    else:
        return jsonify({
            'message': 'invalid request', 'status': 405
        })


@app.route('/histry_get', methods=['GET'])
@token_required
def histry_get(current_user):
    result_cursor = histry_collection.find({}, {'_id': 0})
    print(result_cursor, 'result_cursor')
    result_list = list(result_cursor)

    # print (result_list,'jjjjj')
    response_data = {'DATA': result_list}
    return jsonify(response_data)
    # if result_list:
    #     # Using json_util to handle BSON serialization, including ObjectId
    #     return jsonify({'data': json_util.dumps(result_list)})
    # else:
    #     return jsonify({
    #         'message': 'No history data found',
    #         'status': 404
    #     })

######################## type bar ###################################################################

# @app.route('/type_bar_post', methods=['POST'])
# def type_bar_post():
#     data = request.form.to_dict()  # Assuming the data is sent as JSON in the request body

#     Level = data.get('Level')
#     Qual = data.get('Qual')
#     Cell = data.get('Cell')
#     Tech = data.get('Tech')
#     Snr = data.get('Snr')
#     Dlrate = data.get('Dlrate')
#     Ulrate = data.get('Ulrate')
#     Speed = data.get('Speed')
#     Latitude=float(data.get('Latitude'))
#     Longitude=float(data.get('Longitude'))

#     if data:
#         # Insert data into the MongoDB collection
#         location_data = {
#             'Level': Level,
#             'Qual': Qual,
#             'Cell': Cell,
#             'Tech': Tech,
#             'Snr': Snr,
#             'Dlrate': Dlrate,
#             'Ulrate': Ulrate,
#             'Speed': Speed,
#             'Latitude':Latitude,
#             'Longitude':Longitude

#         }

#         type_bar_collection.insert_one(location_data)

#         return jsonify('response_data'), 201
#     else:
#         return jsonify({'message': 'Please provide a valid level parameter'}), 400


@app.route('/type_bar_post', methods=['POST'])
@token_required
def type_bar_post(current_user):
    # Assuming the data is sent as JSON in the request body
    data = request.form.to_dict()

    LEVEL = data.get('LEVEL')
    QUAL = data.get('QUAL')
    CELL = data.get('CELL')
    TECH = data.get('TECH')
    SNR = data.get('SNR')
    DLRATE = data.get('DLRATE')
    ULRATE = data.get('ULRATE')
    SPEED = data.get('SPEED')
    date = data.get('date')

    # Check if 'Latitude' key exists and its value is not None
    latitude = float(data.get('latitude')) if 'latitude' in data and data.get(
        'latitude') is not None else None

    # Check if 'Longitude' key exists and its value is not None
    longitude = float(data.get('longitude')) if 'longitude' in data and data.get(
        'longitude') is not None else None

    if all([LEVEL, QUAL, CELL, TECH, SNR, DLRATE, ULRATE, date, SPEED, latitude is not None, longitude is not None]):
        # Insert data into the MongoDB collection
        location_data = {
            'date': date,
            'LEVEL': LEVEL,
            'QUAL': QUAL,
            'CELL': CELL,
            'TECH': TECH,
            'SNR': SNR,
            'DLRATE': DLRATE,
            'ULRATE': ULRATE,
            'SPEED': SPEED,
            'latitude': latitude,
            'longitude': longitude

        }

        type_bar_collection.insert_one(location_data)

        return jsonify({'message': 'Data inserted successfully', 'status': 200}), 201
    else:
        return jsonify({'message': 'Please provide valid data for all parameters, including Latitude and Longitude', 'status': 400}), 400


# @app.route('/type_bar_get/<key>', methods=['GET', 'POST'])
# def type_bar_get(key):

#     result = type_bar_collection.find({key: {'$exists': True}}, {'_id': 0, key: 1})

#     if result:
#         return jsonify({'data': {key: result[key]}})
#     else:
#         return jsonify({'message': f'No data found for the specified key: {key}'}), 404


# @app.route('/type_bar_get/<key>', methods=['GET', 'POST'])
# def type_bar_get_all_levels(key):
#     result_cursor = type_bar_collection.find({key: {'$exists': True}}, {'_id': 0, key: 1})
#     result_list = list(result_cursor)

#     if result_list:
#         values = [doc[key] for doc in result_list]
#         return jsonify({'data': {key: values}})
#     else:
#         return jsonify({f'message': 'No data found for the specified key: {key}'}), 404


# @app.route('/type_bar_get/<key>', methods=['GET', 'POST'])
# def type_bar_get_all_levels(key):
#     # Find all documents where the specified key exists
#     result_cursor = type_bar_collection.find({key: {'$exists': True}}, {'_id': 0})
#     result_list = list(result_cursor)

#     if result_list:
#         # Extract the specified key, 'Latitude', and 'Longitude' fields from each document in the list
#         data = {k: [doc[k] for doc in result_list] for k in [key]},['latitude', 'longitude']
#         return jsonify({'data': data})
#     else:
#         return jsonify({'message': f'No data found for the specified key: {key}'}), 404

# @app.route('/get_csv', methods=['GET'])
# def get_csv():
#     find_data = type_bar_collection.find({}, {'_id': 0})
#     if find_data:
#         dd=pd.DataFrame(find_data)
#         print(dd,'lkjhgfdsa')
#         print('kkkk',find_data,'llllll')
#         csv_filename = "type_bar.csv"
#         dd.to_csv(csv_filename, index=False)
#         return  csv_filename


@app.route('/get_excel', methods=['GET'])
@token_required
def get_excel():
    find_data = type_bar_collection.find({}, {'_id': 0})
    if find_data:
        df = pd.DataFrame(find_data)
        excel_filename = "type_bar.xlsx"
        df.to_excel(excel_filename, index=False)
        # print('downloaded')
        return send_file(excel_filename, as_attachment=True)
    else:
        return "No data found."


# from flask import jsonify
@app.route('/type_bar_get/<key>', methods=['GET', 'POST'])
# @token_required
def type_bar_get_all_levels(key):
    # return key
    aggr = [
        {
            '$project': {
                key: 1,
                'latitude': 1,
                'longitude': 1
            }
        }
    ]
    # result_cursor = type_bar_collection.find({key: {'$exists': True}}, {'_id': 1, key: 1, 'latitude': 1, 'longitude': 1})
    result_cursor = type_bar_collection.aggregate(aggr)
    result_list = list(result_cursor)

    print(result_list)

    if result_list:

        data = [{'_id': str(doc['_id']), 'type': doc[key], "network_type": key,
                 'latitude': doc['latitude'], 'longitude': doc['longitude']} for doc in result_list]
        return jsonify({'data': data})
    else:
        return jsonify({'message': f'No data found for the specified key: {key}'}), 404

############# Feedback############################################################################


@app.route('/feedback', methods=['POST'])
@token_required
def feedback(current_user):
    if request.method == 'POST':
        fdBack = request.form.get('fdBack')
        comment = request.form.get('comment')

        feedback = {
            'fdBack': fdBack,
            'comment': comment
        }
        print(feedback, 'feedback')
        feedback_collection.insert_one(feedback)
        return jsonify({
            'msg': 'Feedback successfull', 'status': 200
        })
    else:
        return jsonify({
            'msg': 'Please send me feedback!', 'status': 400
        })


################## Admiin APIs #########################################################################
# import base64

def admin_required(f):
    @wraps(f)
    def decorator2(*args, **kwargs):

        token = None
        if "Authorization" in request.headers:
            token = request.headers["Authorization"].split(" ")[-1]
            # print(token,"dasgfhgfsahgdfsahgd")
            print("recieved token", token)
        if not token:
            return jsonify({"message": " valid token is missing", 'status': 400})

        try:
            data = jwt.decode(
                token,
                algorithms="HS512",
                key="GameDev",
            )
            print("dsifhsdkuhfkusdhfkuhsd", data)

            aggr = [
                {
                    '$match': {
                        '_id': ObjectId(data['userDetails']['_id'])
                    }
                    # '$match': {
                    #     '_id': ObjectId(data['user_id'])
                    # }
                }, {
                    '$addFields': {
                        '_id': {
                            '$toString': '$_id'
                        }
                    }
                }
            ]
            print(aggr, 'aggr')

            admin_user = list(admin_login_collection.aggregate(aggr))
            print(admin_user, 'admin_user')
            database_data = len(admin_user)
            print(database_data, 'database_data')
            if database_data == 0:
                return jsonify({"message": "no data", 'status': 400})

        except Exception as e:
            print(e)
            return jsonify({"message": "Token is invalid", 'status': 400})
        return f(admin_user[0], *args, **kwargs)

    return decorator2


@app.route('/admin_create_id', methods=['POST'])
def admin():
    if request.method == 'POST':
        # Assuming you're getting user_id from a form field
        admin_id = request.form.get('admin_id')
        admin_password = request.form.get('admin_password')
        # user_id='shobhit.pal@fourbrick.com'
        # user_password='123654'
        admin = {
            'admin_id': admin_id,
            'admin_password': admin_password
        }
        admin_login_collection.insert_one(admin)
        return jsonify({'msg': 'admin id created'})
        # if admin:
        #     print(admin.inserted_id)


@app.route("/admin_login", methods=['POST'])
def admin_login():
    if request.method == "POST":
        admin_id = request.form.get("admin_id")
        admin_password = request.form.get("admin_password")

        user_data = admin_login_collection.find_one(
            {"admin_id": admin_id, 'admin_password': admin_password})
        print(user_data, 'user_data')
        # if user_data:
        #     return jsonify({"message":"Login successful."} )

        # if 'admin_password' in user_data:
        # if user_data['verified']:
        # print('yes')
        if user_data:
            if str(user_data['admin_password']) == str(admin_password):
                user_data['_id'] = str(user_data['_id'])
                del user_data['admin_password']
                access_token = jwt.encode(
                    {
                        "userDetails": user_data, "userId": user_data["_id"]
                    },
                    key="GameDev",
                    algorithm="HS512",
                )
                response = make_response(
                    jsonify({"token": access_token, "user": user_data})
                )
                response.set_cookie(
                    "token",
                    access_token,
                    # secure=True,
                    httponly=True,
                    samesite=None,

                )
                data = jwt.decode(
                    access_token,
                    algorithms="HS512",
                    key="GameDev",
                )
                print(data, 'access_token')
                return jsonify({"message": "Login successful.", "token": access_token, "token_Data": data, 'status': 200})

        else:
            return jsonify({"message": "Admin Not found", 'status': 400})
    else:
        return jsonify({"message": "User Id wrong...", 'status': 400})


@app.route('/find_users', methods=['GET', 'POST'])
# @admin_required
def find_user():
    print()
    # print(admin_user, 'admin_user')
    if request.method == 'GET':
        # print('get')
        # username = request.args.get('username')
        agr = [
            {
                '$project': {
                    'username': 1,
                    'email': 1,
                    '_id': {'$toString':'$_id'}
                }
            }
        ]

        users = list(signup_data.aggregate(agr))
        # print(users, 'usersusers')

        return jsonify(users)

    # else:
    #     print('jbhy')
    return jsonify({'msg': 'method invalid'})






@app.route('/find_user_data/<user_id>', methods=['GET'])
def find_user_data(user_id):
    print(user_id,'useriduhg')
    try:
        user_object_id = ObjectId(user_id)
    except Exception as e:
        return jsonify({'message': f'Invalid user_id: {str(e)}'}), 400

    user_data = signup_data.find_one({'_id': user_object_id})

    if user_data:
        aggregation_pipeline = [
            {
                '$match': {
                    '_id': user_object_id
                }
            },
            {
                '$project': {
                    '_id': 1,
                    'date': 1,
                    'LEVEL': 1,
                    'QUAL': 1,
                    'CELL': 1,
                    'TECH': 1,
                    'SNR': 1,
                    'DLRATE': 1,
                    'ULRATE': 1,
                    'SPEED': 1,
                    'latitude': 1,
                    'longitude': 1
                }
            }
        ]

        
        type_bar_data = list(type_bar_collection.aggregate(aggregation_pipeline))

        if type_bar_data:
            
            result = {
                'user_data': user_data,
                'type_bar_data': type_bar_data
            }
            return jsonify(result)
        else:
            return jsonify({'message': 'No matching data found in type_bar collection'}), 404
    else:
        return jsonify({'message': 'User not found in signup collection'}), 404


if __name__ == '__main__':
    app.run(debug=True, port=8020)



# @app.route('/find_location', methods=['POST', 'GET'])
# def find_location():
#     if request.method == 'POST':
#         lat = request.form.get('lat')
#         lon = request.form.get('long')
#         return jsonify({'lat': lat, 'long': lon})
#     else:
#         return jsonify({'msg': 'Method not found'}), 404
#         pass
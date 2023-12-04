import json
import pymysql

def lambda_handler(event, context):
    print(event)
   

    seltable = event['queryStringParameters']['datatable']
    username = event['queryStringParameters']["username"]
    #seltable = event["pathParameters"]["parameter1"]
    try:
        # Connect to SQL server
        db_host = 'sattrack.ckiq4qoeqhbu.us-east-2.rds.amazonaws.com'
        db_name = 'SatTracker'
        db_user = 'admin'
        db_password = 'SatTracker23'
        
        con3 = pymysql.connect(host=db_host, user=db_user, password=db_password, database=db_name, connect_timeout=10)
        
        # Query the database
        cursor = con3.cursor()
        
        dataquery = "SELECT satName, satCat, lat, lng, alt from " +  seltable
        cursor.execute(dataquery)
        data = cursor.fetchall()
        
        ####Now get user favorites####
        print(username)
        userquery = "SELECT favSat FROM users2 WHERE username = %s"
        cursor.execute(userquery, (username,))
        userdata = cursor.fetchall()
        print("user data")
        print(userdata)
        #create dict to separate data
        response_data = {
            'data': data,  # sat info
            'userdata': userdata  #userquery
        }
        response = {
            'statusCode': 200,
            'body': json.dumps(response_data),
            'headers': {
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            }
        }
                    
        cursor.close()
        con3.close()
        
    except Exception as e:
        # Handle any errors that occur during database interaction
        response = {
            "statusCode": 500,  # 500 is the HTTP status code for internal server error
            'body': json.dumps(e)
        }
    print(response)
    return response 
    

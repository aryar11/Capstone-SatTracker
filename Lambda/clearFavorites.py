import json
import pymysql
import boto3
def lambda_handler(event, context):
    request_body = json.loads(event['body'])
    username = request_body.get('username')
    #username = "test"
    con2 = None  # Initialize con2 as None
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': '*',
        'Access-Control-Allow-Methods': '*',
    }
    try:
        # Connect to SQL server
        db_host = 'sattrack.ckiq4qoeqhbu.us-east-2.rds.amazonaws.com'
        db_name = 'SatTracker'
        db_user = 'admin'
        db_password = 'SatTracker23'

        con2 = pymysql.connect(host=db_host, user=db_user, password=db_password, database=db_name, connect_timeout=5)

        # Query the database to check if the user exists
        cursor = con2.cursor()
        find_query = "SELECT username FROM users2 WHERE username = %s"
        cursor.execute(find_query, (username,))
        data = cursor.fetchone()  # Fetch only one row since usernames should be unique
        if data is not None:
            print("Username exists")
            # User with the provided username exists, clear the favSat
            clear_favSat_query = "UPDATE users2 SET favSat = NULL WHERE username = %s"
            cursor.execute(clear_favSat_query, (username,))
            con2.commit()  # Commit the changes
            # Add CORS headers to allow requests from any origin
                    
            s3 = boto3.client(
                's3',
                aws_access_key_id='AKIA2GBQBRJE53N4XPM3',
                aws_secret_access_key='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'
            )
        
            bucket_name = "satdate"
            html_file_path = "https://satdate.s3.us-east-2.amazonaws.com/favoriteData.json"
        
            # Specify the object key for the JSON file in S3
            json_file_key = "favoriteData.json"
            existing_json = [
                                [
                                    "Favorites",
                                    [
                             
                                    ]
                                ]
                            ]
            # Append the new JSON data to the existing structure
            # Convert the updated JSON structure to a string
            updated_json_str = json.dumps(existing_json, indent=4)
            # Upload the updated JSON back to the S3 bucket
            s3.put_object(Bucket=bucket_name, Key=json_file_key, Body=updated_json_str)
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps('favSat cleared for the user.')
            }
        else:
            print("username doesnt exists")
            return {
                'statusCode': 404,  # User not found
                'headers': headers,
                'body': json.dumps('User not found.')
            }
    except Exception as e:
        print("cant connect to sql")
        return {
            'statusCode': 500,  # Internal server error
             'headers': headers,
            'body': json.dumps(f'Error: {str(e)}')
        }
    finally:
        if con2 is not None:
            con2.close()
    
    return {
        'statusCode': 200,
         'headers': headers,
        'body': json.dumps('Hello from Lambda!')
    }

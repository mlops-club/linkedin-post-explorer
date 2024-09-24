import json
import boto3
import sqlite3
import os
from urllib.parse import urlparse

s3 = boto3.client('s3')

# S3 asset path for the SQLite database
S3_POSTS_DB_ASSET_PATH = os.environ['S3_POSTS_DB_ASSET_PATH']

# Parse the S3 URL to get bucket and key
parsed_url = urlparse(S3_POSTS_DB_ASSET_PATH)
S3_BUCKET_NAME = parsed_url.netloc
S3_POSTS_DB_KEY = parsed_url.path.lstrip('/')

# Local path to save the downloaded database
LOCAL_DB_PATH = '/tmp/posts.db'

def download_db_from_s3():
    s3.download_file(S3_BUCKET_NAME, S3_POSTS_DB_KEY, LOCAL_DB_PATH)

# Download the database at module load time
download_db_from_s3()

def execute_query():
    conn = sqlite3.connect(LOCAL_DB_PATH)
    cursor = conn.cursor()
    
    query = """
    SELECT
        author_firstName,
        author_lastName,
        COUNT(*) as num_comments
    FROM comments
    GROUP BY author_firstName, author_lastName 
    ORDER BY num_comments DESC
    """
    
    cursor.execute(query)
    results = cursor.fetchall()
    
    conn.close()
    
    return results

def handler(event, context):
    try:
        # Execute the query
        results = execute_query()
        
        # Convert results to nested dict
        nested_dict = {
            "comments_by_author": [
                {
                    "author_firstName": row[0],
                    "author_lastName": row[1],
                    "num_comments": row[2]
                } for row in results
            ]
        }
        
        return {
            'statusCode': 200,
            'body': json.dumps(nested_dict)
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }


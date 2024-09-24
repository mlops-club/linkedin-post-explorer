import httpx

def send_event():
    # Define the URL of the Lambda runtime API
    url = "http://localhost:9000/2015-03-31/functions/function/invocations"

    # Define a trivial event payload
    event_payload = {
        "key1": "value1",
        "key2": "value2",
        "key3": "value3"
    }

    # Send the event to the Lambda runtime API
    response = httpx.post(url, json=event_payload)

    # Print the response from the Lambda function
    print("Status Code:", response.status_code)
    print("Response Body:", response.text)

if __name__ == "__main__":
    send_event()
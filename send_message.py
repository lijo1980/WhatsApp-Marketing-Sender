from flask import Flask, request, jsonify
import pandas as pd
import requests
import time

app = Flask(__name__)

# Load data from an excel file
def load_data(file_path):
    df = pd.read_excel(file_path)
    print("Column names:", df.columns.tolist())
    return df

# assuming that the excel sheet has column A with phone numbers, column B with body parameters and column C with an image link etc
def send_template_message(access_token, phone_number, body_params, image_link=None, header_text=None, footer_text=None):
    url = 'https://graph.facebook.com/v21.0/169792389547021/messages' #replace the phone_number_id with your WhatsApp API linked numbers phonenumberid
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    # Constructing the components for the template message
    components = []

    # Add header if provided
    if image_link or header_text:
        header_parameters = []
        if image_link:
            header_parameters.append({
                "type": "image",
                "image": {
                    "link": image_link
                }
            })
        if header_text:
            header_parameters.append({
                "type": "TEXT",
                "text": header_text
            })
        
        components.append({
            "type": "header",
            "parameters": header_parameters
        })

    # Adding body parameters from comma-separated values like [ "Amy Johnson", "79546000009452005", "2024-05-24T09:12:31+05:30"]
    body_parameters = []
    for text in body_params.split(','):
        body_parameters.append({
            "type": "TEXT",
            "text": text.strip()
        })

    components.append({
        "type": "body",
        "parameters": body_parameters
    })

    # Add a footer value if provided and has a variable in the template
    if footer_text:
        components.append({
            "type": "footer",
            "parameters": [
                {
                    "type": "TEXT",
                    "text": footer_text
                }
            ]
        })

    payload = {
        "messaging_product": "whatsapp",
        "to": phone_number,
        "recipient_type": "individual",
        "type": "template",
        "template": {
            "name": "wemissyou", #the name of your template
            "language": {
                "code": "en_US" #please ensure you have the correct language code based on your template selection
            },
            "components": components
        }
    }

    response = requests.post(url, headers=headers, json=payload)
    return response.json()

@app.route('/send-messages', methods=['POST'])
def send_messages():
    
    ACCESS_TOKEN = 'EAACadsoEimMBOZBzkpc81EQ3i0oK6RgKZBq0fYZCNnHhkuelOKFugJynJyNVqFtUic1yIDPhLeIcBOUQiBrLGGdeLT3p9E7xGLpusNgfzTvZCZAg00WGkaGC5LVsWQZBraRxksGW0wZAheitZCBe65GrayRZByZBuHRVBQDddjBzZCyJl3oov2yDUYZBz6QOTVUwyZALP' #This is the API token for your WhatsApp

    # Geting parameters from the request from the excel file
    file_path = request.json.get('file_path') #path_to_your_excel_file.xlsx is the path of your excel file
    if not file_path:
        return jsonify({"error": "file_path is required"}), 400

    # Load data from Excel file
    df = load_data(file_path)

    try:
        df = load_data(file_path)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    results = []

    # for each row in the excel sheet, sending template messages
    for index, row in df.iterrows():
        phone_number = row['Phone_Number']
        body_params = row.get('Body')  # Comma-separated values
        image_link = row.get('Image', '')  # Optional image link
        header_text = row.get('Header_Text', '')  # Optional header text
        footer_text = row.get('Footer_Text', '')   # Optional footer text

        # Ensure none of the parameters are NaN
        body_params = body_params if pd.notna(body_params) else ''
        image_link = image_link if pd.notna(image_link) else ''
        header_text = header_text if pd.notna(header_text) else ''
        footer_text = footer_text if pd.notna(footer_text) else ''

        result = send_template_message(ACCESS_TOKEN, phone_number, body_params, image_link, header_text, footer_text)
        results.append(result)

        time.sleep(1)  # it is recommended to add a pause between your messages, I have added 1 second, adjust the time as needed

    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)

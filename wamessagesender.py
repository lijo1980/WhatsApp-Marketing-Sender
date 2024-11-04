import pandas as pd
import requests
import time
import os
import argparse

def load_data(file_path):
    df = pd.read_excel(file_path)
    return df

def send_template_message(access_token, phone_number, body_params, image_link=None, header_text=None):
    url = 'https://graph.facebook.com/v21.0/<phone_number_id>/messages' #update Phone Number Id here
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    components = []
    
    if image_link or header_text:
        header_parameters = []
        if image_link:
            header_parameters.append({"type": "image", "image": {"link": image_link}})
        if header_text:
            header_parameters.append({"type": "TEXT", "text": header_text})
        
        components.append({"type": "header", "parameters": header_parameters})

    body_parameters = [{"type": "TEXT", "text": text.strip()} for text in body_params.split(',')]
    components.append({"type": "body", "parameters": body_parameters})

    payload = {
        "messaging_product": "whatsapp",
        "to": phone_number,
        "recipient_type": "individual",
        "type": "template",
        "template": {
            "name": "wemissyou",
            "language": {"code": "en_US"},
            "components": components
        }
    }

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code != 200:
        return {"error": response.text, "status_code": response.status_code}
    else:
        print(f"Response {response.json()}")
    return

def main(file_path):
    # ACCESS_TOKEN = os.getenv('WHATSAPP_ACCESS_TOKEN')
    ACCESS_TOKEN = "ACCESS_TOKEN" #Enter Access Token here

    # Load data from the Excel file
    try:
        df = load_data(file_path)
    except Exception as e:
        print(f"Error loading data: {e}")
        return

    results = []

    # Send messages for each row in the Excel sheet
    for index, row in df.iterrows():
        phone_number = row['Phone_Number']
        body_params = row.get('Body', '')  # Comma-separated values
        image_link = row.get('Image', '')  # Optional image link
        header_text = row.get('Header_Text', '')  # Optional header text

        # Ensure none of the parameters are NaN
        body_params = body_params if pd.notna(body_params) else ''
        image_link = image_link if pd.notna(image_link) else ''
        header_text = header_text if pd.notna(header_text) else ''

        result = send_template_message(ACCESS_TOKEN, phone_number, body_params, image_link, header_text)
        results.append(result)

        time.sleep(1)  # Sleep to avoid hitting rate limits

    # print("Results:", results)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Send WhatsApp messages from an Excel file.')
    parser.add_argument('file_path', type=str, help='Path to the Excel file')
    args = parser.parse_args()
    main(args.file_path)

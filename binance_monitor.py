import requests
import json
import pandas as pd
import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os

def send_email(text, recipients):
    """Send email with the stock updates"""
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    sender_email = os.environ['SENDER_EMAIL']
    sender_password = os.environ['EMAIL_PASSWORD']
    
    # Create the email content
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['Subject'] = 'New Stocks Added to Trading212'
    msg.attach(MIMEText(text, 'plain'))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipients, msg.as_string())
        print("Email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")
    finally:
        server.quit()

def main():

    url = "https://api.binance.com/api/v3/ticker/price"
    response = requests.get(url)


    if response.status_code == 200:
        # get the up to date list of symbols
        current_symbols_list = []
        for symbol in response.json():
            if symbol['symbol'].endswith('USDT'):
                current_symbols_list.append(symbol['symbol'])

        # load the current list of symbols from file

        with open("binance_symbols.json", "r") as file:
            try:
                old_symbols_list = json.load(file)
            except json.JSONDecodeError:
                old_symbols_list = []  # Default to an empty list if the file is invalid/empty

        # check if there are any new symbols not on the current symbols list
        new_symbols  = set(current_symbols_list) - set(old_symbols_list)


        # If there are any, add them to the new_symbols json, add them to the current symbols json and send out an email

        if len(new_symbols) > 0:
            # first update the binance_symbols list
            with open("binance_symbols.json", "w") as file:
                json.dump(current_symbols_list, file)

            # now update the new_symbols list

            with open("new_symbols.json", "r") as file:
                try:
                    new_symbols_dict = json.load(file)
                except json.JSONDecodeError:
                    new_symbols_dict = []  # Default to an empty list if the file is invalid/empty
            for symbol in new_symbols:
                new_symbols_dict.append({'symbol':symbol,'date':datetime.datetime.now().strftime('%Y-%m-%d %H:%M')})

            # Create email content
                header = 'New symbols added to Binance:\n\n'
                text = header + new_symbols_dict

            # save the new_symbols_dict
            with open("new_symbols.json", "w") as file:
                json.dump(new_symbols_dict, file)

            # Get recipients from environment variable
            recipients = json.loads(os.environ['RECIPIENTS'])
            
            # Send email
            send_email(text, recipients)
        else:
            print("No new symbols found")
    else:
        print(f"Error fetching data: {response.status_code}")

if __name__ == "__main__":
    main()

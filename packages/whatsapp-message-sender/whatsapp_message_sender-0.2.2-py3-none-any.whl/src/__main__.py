import argparse
import time
import pandas as pd
from urllib.parse import quote
from platform import system 
import webbrowser as web
import pyautogui as pg

def close_tab(wait_time: int = 2) -> None:
    """Closes the Currently Opened Browser Tab"""
    if system().lower() in ("windows", "linux"):
        pg.hotkey("ctrl", "w")
        pg.press("enter")
    elif system().lower() in "darwin":
        pg.hotkey("command", "w")
        pg.press("enter")
    else:
        raise Warning(f"{system().lower()} not supported!")

def sendwhatmsg_instantly(phone_no: str, message: str, wait_time: int, tab_close: bool, close_time: int):
    """Send WhatsApp Message Instantly"""
    parsed_message = quote(message) 
    url = 'https://web.whatsapp.com/send?phone='+phone_no+'&text=' + parsed_message + '&app_absent=1'
    print(url)
    web.open(url)
    time.sleep(wait_time)
    pg.press('enter')
    time.sleep(1)
    if tab_close:
        close_tab(wait_time=close_time)

def find_empty_payments(file_path: str, phone_field: str, payment_field: str) -> list:
    """Read CSV file, find rows with empty 'payment', add phone numbers to a list"""
    df = None
    if file_path.endswith('.xlsx'):
        df = pd.read_excel(file_path)
    elif file_path.endswith('.csv'): 
        df = pd.read_csv(file_path)
    empty_payments = df[df[payment_field].isna()]
    phone_numbers = empty_payments[phone_field].tolist()
    return phone_numbers

def send_bulk_messages(phone_numbers, message, wait_time=10, close_tab_wait_time=3):
    for phone in phone_numbers:
        sendwhatmsg_instantly(str(phone), message, wait_time, True, close_tab_wait_time)
        
def run(clients_file, message_file, wait_time, close_tab_wait_time, phone_field, payment_field):
    with open(message_file, 'r', encoding='utf-8') as file:
        message = file.read()
    phones_with_empty_payments = find_empty_payments(clients_file, phone_field, payment_field)
    send_bulk_messages(phones_with_empty_payments, message, wait_time, close_tab_wait_time)

def main():
    parser = argparse.ArgumentParser(description='Send WhatsApp messages to clients with pending payments.')
    parser.add_argument('--file', required=True, help='Path to the CSV file with client data')
    parser.add_argument('--message', required=True, help='Path to the TXT file with the message')
    parser.add_argument('--wait', default=10, type=int, help='Wait time between opening WhatsApp web and sending the message')
    parser.add_argument('--close_wait', default=3, type=int, help='Wait time before closing the tab')
    parser.add_argument('--phone_field', default='phone', help='Name of the field containing phone numbers')
    parser.add_argument('--payment_field', default='payment', help='Name of the field indicating payment status')

    args = parser.parse_args()
    
    run(args.file, args.message, args.wait, args.close_wait, args.phone_field, args.payment_field)

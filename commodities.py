import json
import os
import smtplib
import time
import requests
import threading
from email.mime.text import MIMEText
import customtkinter as ctk
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
email_sender = os.getenv("EMAIL_SENDER")
email_password = os.getenv("EMAIL_PASSWORD")
email_receiver = os.getenv("EMAIL_RECEIVER")

price_history = {}

class CommodityApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Live Commodity Prices w/ Alerts")
        self.geometry("500x500")
        self.configure(bg="#2C2F33")
        ctk.set_appearance_mode("dark")

        self.title_label = ctk.CTkLabel(self, text="Live Commodity Prices w/ Alerts", font=("Arial", 18, "bold"))
        self.title_label.pack(pady=10)
        self.frame = ctk.CTkFrame(self)
        self.frame.pack(pady=10, fill="both", expand=True)

        self.commodity_labels = {}
        self.commodities = [
            "WTI", "BRENT", "NATURAL_GAS", "COPPER", "ALUMINUM", "WHEAT", "CORN", "COTTON", "SUGAR", "COFFEE", "ALL_COMMODITIES"
        ]
        self.update_commodity_prices()

    def update_commodity_prices(self):
        for commodity in self.commodities:
            price, timestamp = get_commodity_price(commodity)
            if price:
                self.update_commodity(commodity, price, timestamp)
        self.after(30000, self.update_commodity_prices)  # Refresh every 30 seconds

    def update_commodity(self, commodity, price, timestamp):
        if commodity not in price_history:
            price_history[commodity] = []
        
        price_history[commodity].append((timestamp, price))
        current_time = int(time.time())
        
        price_history[commodity] = [(t, p) for t, p in price_history[commodity] if current_time - t <= 60]
        
        if len(price_history[commodity]) >= 2:
            initial_price = price_history[commodity][0][1]  
            percent_change = ((price - initial_price) / initial_price) * 100
            if abs(percent_change) >= 3:
                send_email_alert(commodity, price, percent_change)

        if commodity not in self.commodity_labels:
            frame = ctk.CTkFrame(self.frame)
            frame.pack(pady=5, fill="x")
            label = ctk.CTkLabel(frame, text=f"{commodity} - ${price}", font=("Arial", 14))
            label.pack(side="left", padx=10)
            self.commodity_labels[commodity] = label
        else:
            self.commodity_labels[commodity].configure(text=f"{commodity} - ${price}")

def get_commodity_price(commodity):
    url = f"https://www.alphavantage.co/query?function={commodity}&interval=monthly&apikey={api_key}"
    response = requests.get(url)
    data = response.json()
    
    time_series = data.get("data", [])
    if not time_series:
        return None, None
    
    latest_data = time_series[0]
    price = float(latest_data["value"])
    return price, int(time.time())

def send_email_alert(commodity, price, percent_change):
    subject = f"ALERT: {commodity} price changed by {percent_change:.2f}%"
    body = f"The commodity {commodity} has changed by {percent_change:.2f}% in the last minute.\nCurrent price: ${price}"
    
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = email_sender
    msg["To"] = email_receiver
    
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(email_sender, email_password)
            server.sendmail(email_sender, email_receiver, msg.as_string())
        print(f"ALERT SENT: {commodity} changed by {percent_change:.2f}%")
    except Exception as e:
        print(f"Failed to send email :(  {e}")

app = CommodityApp()
app.mainloop()

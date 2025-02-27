
import websocket
import json
import asyncio
import threading
import os
import smtplib
import time
from email.mime.text import MIMEText
import customtkinter as ctk
from dotenv import load_dotenv

load_dotenv()



'''
sample api response :p


{
"data": [
  {
    "p": 7296.89,
    "s": "BINANCE:BTCUSDT",
    "t": 1575526691134,
    "v": 0.011467
  }
],
"type": "trade"
}


'''


api_key = os.getenv("API_KEY")
email_sender = os.getenv("EMAIL_SENDER")
email_password = os.getenv("EMAIL_PASSWORD")
email_receiver = os.getenv("EMAIL_RECEIVER")

price_history = {}
class StockApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("live stock price w alerts")
        self.geometry("500x500")
        self.configure(bg="#2C2F33")
        ctk.set_appearance_mode("dark")

        self.title_label = ctk.CTkLabel(self, text="live quote w alerts", font=("Arial", 18, "bold"))
        self.title_label.pack(pady=10)
        self.frame = ctk.CTkFrame(self)
        self.frame.pack(pady=10, fill="both", expand=True)

        self.stock_labels = {}  

    def update_stock(self, symbol, price, timestamp, volume):
        if symbol not in price_history:
            price_history[symbol] = []
        
        price_history[symbol].append((timestamp, price))
        
        #time in miliseconds 
        current_time = int(time.time() * 1000)  

        
        price_history[symbol] = [(t, p) for t, p in price_history[symbol] if current_time - t <= 60000]

        if len(price_history[symbol]) >= 2:
            initial_price = price_history[symbol][0][1]  
            percent_change = ((price - initial_price) / initial_price) * 100


            #check for % chng. to break 3 to send email
            if abs(percent_change) >= 3:  
                send_email_alert(symbol, price, percent_change)

        if symbol not in self.stock_labels:
            frame = ctk.CTkFrame(self.frame)
            frame.pack(pady=5, fill="x")
            label = ctk.CTkLabel(frame, text=f"{symbol} - ${price}", font=("Arial", 14))
            label.pack(side="left", padx=10)
            volume_label = ctk.CTkLabel(frame, text=f"volume: {volume}", font=("Arial", 12))
            volume_label.pack(side="right", padx=10)
            self.stock_labels[symbol] = (label, volume_label)
        else:
            self.stock_labels[symbol][0].configure(text=f"{symbol} - ${price}")
            self.stock_labels[symbol][1].configure(text=f"volume: {volume}")

# function to send email alert
def send_email_alert(symbol, price, percent_change):
    subject = f"ALERT : {symbol} price changed by {percent_change:.2f}%"
    body = f"the stock {symbol} has changed by {percent_change:.2f}% in the last minute.\ncurrent price: ${price}"

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = email_sender
    msg["To"] = email_receiver

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(email_sender, email_password)
            server.sendmail(email_sender, email_receiver, msg.as_string())
        print(f"ALERT SENT: {symbol} changed by {percent_change:.2f}%")
    except Exception as e:
        print(f"Failed to send email :(  {e}")

def on_message(ws, message):
    global app
    msg_dict = json.loads(message)

    if "data" in msg_dict:
        for trade in msg_dict["data"]:
            price = trade["p"]
            symbol = trade["s"]
            timestamp = trade["t"]
            volume = trade["v"]

            app.after(0, app.update_stock, symbol, price, timestamp, volume)


#websocket function to print stderr.
def on_error(ws, error):
    print(f"Error: {error}")


# requiref function for websocket connection
def on_close(ws, close_status_code, close_msg):
    print("### WebSocket Closed ###")


def on_open(ws):
    symbols = ["BINANCE:ADAUSDT", "AAPL", "AMZN", "BINANCE:BTCUSDT", "TSLA", "MSFT", "GOOG", "META", "BINANCE:ETHUSDT", "WMT", "KO", "PFE" ]
    for symbol in symbols:
        ws.send(json.dumps({"type": "subscribe", "symbol": symbol}))

def start_websocket():
    ws = websocket.WebSocketApp(f"wss://ws.finnhub.io?token={api_key}", on_message=on_message, on_error=on_error,on_close=on_close)
    ws.on_open = on_open
    ws.run_forever()

ws_thread = threading.Thread(target=start_websocket, daemon=True)
ws_thread.start()
app = StockApp()
app.mainloop()

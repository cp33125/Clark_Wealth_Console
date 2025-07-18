import tkinter as tk
import requests
import threading
import time

# === TELEGRAM ALERTS ===
def send_telegram_alert(message):
    bot_token = "7938878501:AAGPS8s1Ifn9LthkY6JcDF3lnKSCHoUHwbw"
    user_id = "6915012464"
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": user_id, "text": message}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"Telegram Error: {e}")

# === SETTINGS ===
UPDATE_INTERVAL = 10  # seconds
sell_limit_price = 3070.00  # editable
buy_alert_price = 2930.00   # editable

sell_alerts_on = True
buy_alerts_on = True
realized_profit = 0.00
heartbeat_state = True

# === PRICE FETCHING ===
def fetch_eth_price():
    try:
        response = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=ETHUSDT", timeout=5)
        data = response.json()
        price = float(data['price'])
        api_status = "Binance ✅"
        return price, api_status
    except:
        try:
            response = requests.get("https://api.coinbase.com/v2/prices/ETH-USD/spot", timeout=5)
            data = response.json()
            price = float(data['data']['amount'])
            api_status = "Coinbase 🟠"
            return price, api_status
        except:
            api_status = "API Error ❌"
            return None, api_status

# === UPDATE FUNCTION ===
def update_price():
    global realized_profit, sell_limit_price, buy_alert_price
    price, api_status = fetch_eth_price()
    if price:
        price_var.set(f"ETH Price: ${price:,.2f}")
        api_status_var.set(api_status)

        if sell_alerts_on and price >= sell_limit_price:
            alert_var.set(f"🚨 SELL ALERT: ETH hit ${price:,.2f}")
            send_telegram_alert(f"🚨 SELL ALERT: ETH hit ${price:,.2f}")
        elif buy_alerts_on and price <= buy_alert_price:
            alert_var.set(f"📢 BUY ALERT: ETH dropped to ${price:,.2f}")
            send_telegram_alert(f"📢 BUY ALERT: ETH dropped to ${price:,.2f}")
        else:
            alert_var.set("✅ Monitoring...")
    else:
        price_var.set("ETH Price: Error")
        api_status_var.set(api_status)

    root.after(UPDATE_INTERVAL * 1000, lambda: threading.Thread(target=update_price, daemon=True).start())

# === HEARTBEAT ===
def animate_heartbeat():
    global heartbeat_state
    heartbeat_label.config(text="💠" if heartbeat_state else "💤")
    heartbeat_state = not heartbeat_state
    root.after(1000, animate_heartbeat)

# === TOGGLE & UPDATE ===
def toggle_sell_alerts():
    global sell_alerts_on
    sell_alerts_on = not sell_alerts_on
    sell_button.config(text=f"SELL Alerts: {'ON' if sell_alerts_on else 'OFF'}")

def toggle_buy_alerts():
    global buy_alerts_on
    buy_alerts_on = not buy_alerts_on
    buy_button.config(text=f"BUY Alerts: {'ON' if buy_alerts_on else 'OFF'}")

def clear_position():
    global realized_profit
    realized_profit = 0.00
    profit_var.set(f"Realized Profit: ${realized_profit:.2f}")

def update_thresholds():
    global sell_limit_price, buy_alert_price
    try:
        sell_limit_price = float(sell_entry.get())
        buy_alert_price = float(buy_entry.get())
        alert_var.set("✅ Thresholds updated")
    except ValueError:
        alert_var.set("⚠ Invalid threshold values")

# === GUI ===
root = tk.Tk()
root.title("Clark Wealth Console 4.2")
root.geometry("450x350")
root.configure(bg="#1E1E1E")
root.resizable(False, False)

price_var = tk.StringVar(value="ETH Price: Loading...")
alert_var = tk.StringVar(value="Initializing...")
profit_var = tk.StringVar(value=f"Realized Profit: ${realized_profit:.2f}")
api_status_var = tk.StringVar(value="API: Connecting...")

# Labels
tk.Label(root, textvariable=price_var, font=("Arial", 20), fg="white", bg="#1E1E1E").pack(pady=10)
tk.Label(root, textvariable=profit_var, font=("Arial", 16), fg="lime", bg="#1E1E1E").pack()
tk.Label(root, textvariable=alert_var, font=("Arial", 14), fg="cyan", bg="#1E1E1E").pack(pady=5)
tk.Label(root, textvariable=api_status_var, font=("Arial", 12), fg="orange", bg="#1E1E1E").pack()

# Heartbeat label
heartbeat_label = tk.Label(root, text="💠", font=("Arial", 20), fg="skyblue", bg="#1E1E1E")
heartbeat_label.pack(pady=5)

# Editable thresholds
tk.Label(root, text="SELL Alert Price ($):", fg="white", bg="#1E1E1E").pack()
sell_entry = tk.Entry(root, font=("Arial", 12), justify="center")
sell_entry.insert(0, str(sell_limit_price))
sell_entry.pack()

tk.Label(root, text="BUY Alert Price ($):", fg="white", bg="#1E1E1E").pack()
buy_entry = tk.Entry(root, font=("Arial", 12), justify="center")
buy_entry.insert(0, str(buy_alert_price))
buy_entry.pack()

tk.Button(root, text="Update Thresholds", command=update_thresholds, font=("Arial", 12), bg="green", fg="white").pack(pady=5)

# Buttons
sell_button = tk.Button(root, text="SELL Alerts: ON", command=toggle_sell_alerts, font=("Arial", 12), bg="#007ACC", fg="white")
sell_button.pack(pady=3)

buy_button = tk.Button(root, text="BUY Alerts: ON", command=toggle_buy_alerts, font=("Arial", 12), bg="#007ACC", fg="white")
buy_button.pack(pady=3)

clear_button = tk.Button(root, text="Clear Position", command=clear_position, font=("Arial", 12), bg="red", fg="white")
clear_button.pack(pady=5)

exit_button = tk.Button(root, text="Exit", command=root.destroy, font=("Arial", 12), bg="gray", fg="white")
exit_button.pack(pady=5)

# Start background tasks
threading.Thread(target=update_price, daemon=True).start()
animate_heartbeat()

root.mainloop()

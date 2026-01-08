# runs on server to refresh data every 5 minutes
import time
from modules.quant_a.data import load_asset

while True:
    df = load_asset("AAPL")
    df.to_csv("data/aapl.csv")
    time.sleep(300)

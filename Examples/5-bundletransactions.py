import json
import os
import sys

sys.path.insert(1, os.getcwd()) #needed to access resources outside this fold
from TxDefi.Data.TradingDTOs import *
from TxDefi.TxDefiToolKit import TxDefiToolKit

txdefitk = TxDefiToolKit()

with open(r'Examples\MyStrategies\bundlestrategy.json', 'r') as file: #needed to get individual wallet settings
    bundles_settings = json.load(file)
    for setting in bundles_settings:
        swap_settings = SwapOrderSettings.load_from_dict(setting)
        wallet_settings = SignerWalletSettings.load_from_dict(setting)
        token_address = "Giqd62VVBisA3xpw5huKEzXi1jVtpxvsAMM4LPQz3j84" #or read it from the json

        bundled_swap_order = BundledSwapOrder(TradeEventType.BUY, token_address, swap_settings, wallet_settings)

        #Buy Bundle
        signatures = txdefitk.trades_manager.execute(bundled_swap_order, 3)

        if signatures:
            print("Bundle Buy was Successful. See the transactions here:")
            for signature in signatures:
                print("Tx: https://solscan.io/tx/" + signature)

        txdefitk.join() #Keep running until user shuts it down

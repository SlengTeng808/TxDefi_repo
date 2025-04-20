import os
import sys

sys.path.insert(1, os.getcwd()) #needed to access resources outside this folder
from TxDefi.TxDefiToolKit import TxDefiToolKit
from TxDefi.Data.TradingDTOs import *
from TxDefi.Data.MarketDTOs import *
txdefitk = TxDefiToolKit()

#Use case: We retrieved a wallet event from a wallet we are watching and want to see what dev bought or sold
example_tx_signature = "2C2tgxkg45zWmKMFcyJGPGEkoTjT6zx5YCnFbsNULgyKex8cX7nkFHZW9dCCefhSQ4SpwVaseLUT1UpwxA7XrLBP"

dev_address = "6nvQzVF8szxrakN38hDhtiCAD6HtJYkALqiyeH2pcR8r"
swap_infos = txdefitk.trades_manager.get_swap_info(example_tx_signature, dev_address, 3)

if swap_infos:
    for swap_info in swap_infos:
        if swap_info.token_balance_change > 0:                
            print(f"{swap_info.payer_address} bought {swap_info.token_address}: {swap_info.token_balance_change} tokens")
        else:
            print(f"{swap_info.payer_address} sold {swap_info.token_address}: {abs(swap_info.token_balance_change)} tokens")

txdefitk.join()
import os
import sys

sys.path.insert(1, os.getcwd()) #needed to access resources outside this fold
import time
from TxDefi.TxDefiToolKit import TxDefiToolKit
from TxDefi.Data.TradingDTOs import *

txdefitk = TxDefiToolKit()

token_address = "Giqd62VVBisA3xpw5huKEzXi1jVtpxvsAMM4LPQz3j84"
sol_buy_amount = Amount.sol_ui(.001)
slippage = Amount.percent_ui(5)
priority_fee = Amount.sol_ui(.0004)

swap_settings = SwapOrderSettings(sol_buy_amount, slippage, priority_fee)
order = SwapOrder(TradeEventType.BUY, token_address, swap_settings)

#Make Transaction
tx_signatures = txdefitk.trades_manager.execute(order)

#Verify Completion
if tx_signatures and len(tx_signatures):
    start_time = time.time()
    transaction_info_list = txdefitk.trades_manager.get_swap_info_default_payer(tx_signatures[0], 3) 

    if transaction_info_list and len(transaction_info_list) > 0:               
        execution_time = time.time() - start_time
        print(f"Received Tx Info for {tx_signatures[0]}")
        print(f"Execution time: {execution_time:.6f} seconds")
        transaction_info_list[0].print_swap_info()                            
    else:
        print("Tx Failed")

#verify order
#Check trade amount
txdefitk.join() #Keep running until user shuts it down


import os
import sys

sys.path.insert(1, os.getcwd()) #needed to access resources outside this folder
from TxDefi.Data.TradingDTOs import *
from TxDefi.TxDefiToolKit import TxDefiToolKit

txdefitk = TxDefiToolKit()
#Make sure your necessary fields are defined. This will error out if that's not right. Detailed video on this will be coming soon
strategy_ids = txdefitk.trades_manager.run_strategies(r'Examples\MyStrategies\strategies.json')

if strategy_ids:
    for id in strategy_ids:
        print("Active Strategy id: " + str(id))

txdefitk.join() #Keep running until user shuts it down

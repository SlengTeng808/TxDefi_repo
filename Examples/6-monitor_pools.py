import time
import os
import sys

sys.path.insert(1, os.getcwd()) #needed to access resources outside this fold
from TxDefi.Data.TradingDTOs import *
from TxDefi.Data.MarketDTOs import *
from TxDefi.Data.TransactionInfo import *
from TxDefi.Abstractions.AbstractTradesManager import AbstractTradesManager
from TxDefi.Abstractions.AbstractTradingStrategy import AbstractTradingStrategy
from TxDefi.TxDefiToolKit import TxDefiToolKit
import TxDefi.Data.Globals as globals

class PoolTrackerPro(AbstractTradingStrategy[MarketAlert]):
    def __init__(self, trades_manager: AbstractTradesManager):       
        AbstractTradingStrategy.__init__(self, trades_manager, [globals.topic_parsed_tx_data])
        #Add these topics to get the transaction feeds from the amm programs if desired ^
        #globals.topic_raylegacy_program_event and globals.topic_raylegacy_program_event 

    def process_event(self, id: int, event: list[MarketAlert]): 
        for event in event:
            print(f"{event.token_address} alert received {event.info_type.name}")
    
    def load_from_dict(self, strategy_settings: dict[str, any]): 
        pass

    def load_from_obj(self, obj: object): 
        pass

    def get_status(self)->str:
        return "PoolTrackerPro"
    
    @classmethod
    def create(self, trades_manager: AbstractTradesManager, settings: dict[str, any] = None)->"PoolTrackerPro":
        return PoolTrackerPro(trades_manager)

    @classmethod
    def custom_schema(cls):
        pass

txdefitk = TxDefiToolKit()
pool_tracker = PoolTrackerPro(txdefitk.trades_manager)
pool_tracker.start()

time.sleep(2)

txdefitk.join() #Keep running until user shuts it down

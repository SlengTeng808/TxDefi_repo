from TxDefi.Data.TradingDTOs import *
from TxDefi.Data.MarketDTOs import *
from TxDefi.Data.TransactionInfo import AccountInfo
from TxDefi.Abstractions.AbstractTradingStrategy import AbstractTradingStrategy
from TxDefi.Abstractions.AbstractTradesManager import AbstractTradesManager
from TxDefi.TxDefiToolKit import TxDefiToolKit

class WalletTrackerPro(AbstractTradingStrategy[AccountInfo]):
    def __init__(self, trades_manager: AbstractTradesManager):       
        AbstractTradingStrategy.__init__(self, trades_manager)

    def process_event(self, id: int, event: AccountInfo):
        tx_sig = self.trades_manager.get_solana_rpc().get_tx_signature_at_slot(event.last_slot)

        if tx_sig:
            print(f"{event.account_address} made a trade! https://solscan.io/tx/{tx_sig}")

    def load_from_dict(self, strategy_settings: dict[str, any]): 
        pass
    
    def load_from_obj(self, obj: object): 
        pass

    def get_status(self)->str:
        return "WalletTrackerPro"

    @classmethod
    def custom_schema(cls):
        pass

    @classmethod
    def create(self, trades_manager: AbstractTradesManager, settings: dict[str, any] = None)->"WalletTrackerPro":
        return WalletTrackerPro(trades_manager)

txdefitk = TxDefiToolKit(True)

wallet_address = "6nvQzVF8szxrakN38hDhtiCAD6HtJYkALqiyeH2pcR8r"
wallet_subscriber = WalletTrackerPro.create(txdefitk.trades_manager)
wallet_subscriber.start()

txdefitk.wallet_tracker.subscribe_to_wallet(wallet_address, wallet_subscriber)
txdefitk.join() #Keep running until user shuts it down


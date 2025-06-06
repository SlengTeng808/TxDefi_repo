import threading
from TxDefi.Abstractions.AbstractTradingStrategy import AbstractTradingStrategy
from TxDefi.Abstractions.AbstractTradesManager import AbstractTradesManager
from TxDefi.Data.MarketDTOs import *
from TxDefi.Data.TradingDTOs import *
import TxDefi.Data.Globals as globals

#Buy or Sell at define MCAP
class McapTargetStrategy(AbstractTradingStrategy):
    def __init__(self, trades_manager: AbstractTradesManager, settings: dict[str, any] = None):
        AbstractTradingStrategy.__init__(self, trades_manager, [globals.topic_token_update_event], settings)
        self.state = StrategyState.RUNNING
        self.event_process_lock = threading.Lock()
 
    def load_from_dict(self, strategy_settings: dict[str, any]):
        order = McapOrder.from_dict(strategy_settings)
        self.load_from_obj(order)
    
    def load_from_obj(self, order: McapOrder):
        self.initial_order = order

        if not self.settings:
            self.settings = order.serialize()

    def process_event(self, id: int, event: any):
        if event == self.initial_order.token_address and self.event_process_lock.acquire(blocking=False):
            token_value = self.trades_manager.get_market_manager().get_token_value(self.initial_order.token_address, Denomination.USD)
            
            if token_value:
                if ((self.initial_order.order_type == TradeEventType.BUY and token_value.market_cap.compare(self.initial_order.target_mcap) >= 0) or
                   (self.initial_order.order_type == TradeEventType.SELL and token_value.market_cap.compare(self.initial_order.target_mcap) <= 0)):
                    
                    if self.initial_order.limit_orders:
                        executable_order = self.initial_order.limit_orders
                        #Make sure to set the base token price
                        executable_order.base_token_price = self.trades_manager.get_market_manager().get_price(self.initial_order.token_address)
                    else:
                        executable_order = SwapOrder(self.initial_order.order_type, self.initial_order.token_address, self.initial_order.swap_settings,
                                            self.initial_order.wallet_settings)
    
                    tx_signatures = self.trades_manager.execute(executable_order, max_tries = 3)
                       
                    if tx_signatures:
                        self.state = StrategyState.COMPLETE                        
                        self.stop()
                        
            self.event_process_lock.release()

    def get_status(self)->str:
        return "Status details" #TODO
    
    @classmethod
    def create(cls, trades_manager: AbstractTradesManager, settings: dict[str, any])->"McapTargetStrategy":
        return McapTargetStrategy(trades_manager, settings) 

    @classmethod
    def custom_schema(cls):
        return OrderWithLimitsStops.schema()
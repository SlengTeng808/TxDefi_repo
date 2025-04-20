import threading
from TxDefi.Data.TradingDTOs import *
from TxDefi.Data.MarketDTOs import *
from TxDefi.Data.TransactionInfo import *
from TxDefi.Abstractions.AbstractTradingStrategy import AbstractTradingStrategy
from TxDefi.Abstractions.AbstractTradesManager import AbstractTradesManager
import TxDefi.Data.Globals as globals
from TxDefi.DataAccess.Blockchains.Solana.RiskAssessor import RiskAssessor
from TxDefi.Utilities import FinanceUtil

class TargetTrade:
    def __init__(self, dev_address: str):
        self.dev_address = dev_address
        self.dev_transactions : list[RetailTransaction] = []
        self.my_buy_amount : Amount = None

class ApingNewTokens(AbstractTradingStrategy):
    def __init__(self, trades_manager: AbstractTradesManager, settings: dict[str, any]):
        AbstractTradingStrategy.__init__(self, trades_manager, [globals.topic_parsed_tx_data], settings)
        self.lock = threading.Lock()
        self.new_tokens : dict[str, ExtendedMetadata] = {}
        self.banned_words = set()
        self.target_trades : dict[str, TargetTrade] = {} #Key=token address

        if settings:
            banned_list = settings.get("banned_words")

            if banned_list:
                for word in banned_list.split(','):
                    self.banned_words.add(word.strip().lower())
        
        self.risk_assessor = RiskAssessor(trades_manager.get_solana_rpc(), self.banned_words)
        self.payer_address = trades_manager.get_default_wallet_settings().get_default_signer().get_account_address()

        max_amount = min(1, self.trades_manager.get_sol_balance().to_ui())
        self.sol_left = Amount.sol_ui(max_amount)#self.trades_manager.get_sol_balance().clone()
        self.default_buy_amount_ui = self.swap_settings.amount.to_ui()

    def process_single_event(self, event: any):
        if (isinstance(event, ExtendedMetadata) and self.sol_left.to_ui() > self.default_buy_amount_ui and event.program_type in self.supported_programs and
         not self.risk_assessor.has_banned_words(event.symbol, event.name, event.description)): #no naughty words :D
            self.new_tokens[event.token_address] = event
        elif isinstance(event, RetailTransaction):
            if event.token_address in self.new_tokens:
                #metadata = self.new_tokens.get(event.token_address)        
                tokens_bought = event.token_quantity
                percent_loss = FinanceUtil.calc_potential_loss_percent(1e9, tokens_bought, event.trade_amt_sol, event.token_reserves)
                self.new_tokens.pop(event.token_address)

                if percent_loss > -.1 and self.lock.acquire(False):
                    print(f"{event.token_address}: Trader {event.trader_address} swapped {event.trade_amt_sol/1e9} SOL. Loss Potential: {percent_loss}")

                    if self.state != StrategyState.COMPLETE:
                        order = SwapOrder(TradeEventType.BUY, event.token_address, self.swap_settings, self.wallet_settings)
                        
                        #order.set_use_signer_amount(True) #Will use defaults if you don't set this
                        #Make Transaction
                        tx_signatures = self.trades_manager.execute(order, 3)
            
                        if tx_signatures and len(tx_signatures) > 0:
                            dev_trade = TargetTrade(event.trader_address)
                            dev_trade.dev_transactions.append(event)

                            self.target_trades[event.token_address] = dev_trade
                            print("Tx Received: " + tx_signatures[0])
                        #self.state = StrategyState.COMPLETE #just do this once as a demonstration
                    self.lock.release()
            elif event.token_address in self.target_trades:
                trade = self.target_trades.get(event.token_address)                
                pnl = self.trades_manager.get_pnl(event.token_address)
                
                if event.is_buy and event.trader_address == self.payer_address: #Register my buy ammount
                    if event.is_buy:                          
                        self.sol_left.add_amount(-event.trade_amt_sol, Value_Type.SCALED)                        
                        trade.my_buy_amount = Amount.tokens_scaled(event.token_quantity, 6) #Get token info if you're not sure what the decimals are      
                    else:
                        self.sol_left.add_amount(event.trade_amt_sol, Value_Type.SCALED)
     
                elif ((event.trader_address == trade.dev_address and not event.is_buy) or #Get out when Dev Sells or Target Pnl is reached
                    (pnl and pnl.pnl_percent.to_ui() >= self.target_pnl)):
                    print(f"{event.token_address}: PNL {pnl.pnl_percent.to_ui()}. Selling now!")
                    sell_settings = self.swap_settings.clone()

                    if not trade.my_buy_amount:
                        trade.my_buy_amount = self.trades_manager.get_token_account_balance(event.token_address, self.payer_address)

                    if trade.my_buy_amount:
                        sell_settings.amount = trade.my_buy_amount

                        order = SwapOrder(TradeEventType.SELL, event.token_address, sell_settings, self.wallet_settings)
                        
                        tx_signatures = self.trades_manager.execute(order, 3)
                
                        if tx_signatures and len(tx_signatures) > 0:
                            self.target_trades.pop(event.token_address)
                            print("Tx Received: " + tx_signatures[0])
                        else:
                            print("Tx Failed, try selling manually or implement retry logic.")  
                            pass #try again
                    else:
                        print("Payer doesn't have a token balance for " + event.token_address) 

    #process a subbed event
    def process_event(self, id: int, event: any):
        if isinstance(event, list):
            for single_event in event:
                self.process_single_event(single_event)
        else:
            self.process_single_event(event)

    def load_from_dict(self, strategy_settings: dict[str, any]):
        amm_names = strategy_settings.get("amms", [])
        self.supported_programs : list[SupportedPrograms] = []

        if not amm_names:
            print("ApingNewTokens: No AMMs are configured")
            return
        
        for amm in amm_names:
            program_name = SupportedPrograms.to_enum(amm)
            
            if program_name:
                self.supported_programs.append(program_name)
        self.target_pnl = Amount.percent_ui(strategy_settings.get("target_pnl", 50))
        self.swap_settings = SwapOrderSettings.load_from_dict(strategy_settings)
        self.wallet_settings = SignerWalletSettings.from_dict(strategy_settings)
      
    def load_from_obj(self, obj: object):
        pass

    def get_status(self)->str:
        return f"Status details: SOL Left = {self.sol_left.to_ui()} Num Trades: {len(self.target_trades)}"
    
    @classmethod        
    def create(cls, trades_manager: AbstractTradesManager, settings: dict[str, any])->"ApingNewTokens":
        return ApingNewTokens(trades_manager, settings)

    @classmethod
    def custom_schema(cls):
        ret_schema ={
            "amms": ["PUMPFUN", "PUMPFUN_AMM", "RAYDIUMLEGACY"],
            "banned_words" : "word 1, word 2",
            "target_pnl" : 10
        }

        ret_schema.update(SwapOrderSettings.schema())
        ret_schema.update(SignerWalletSettings.schema())
        
        return ret_schema
        

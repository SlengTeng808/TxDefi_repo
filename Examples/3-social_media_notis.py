import os
import sys

sys.path.insert(1, os.getcwd()) #needed to access resources outside this fold
from TxDefi.Data.TradingDTOs import *
from TxDefi.Data.MarketDTOs import *
from TxDefi.Engines.SocialMediaTracker import SocialMediaTracker
from TxDefi.Abstractions.AbstractTradesManager import AbstractTradesManager
from TxDefi.TxDefiToolKit import TxDefiToolKit

class SocialMediaListener(SocialMediaTracker):
    def __init__(self, trades_manager: AbstractTradesManager):
        SocialMediaTracker.__init__(self, trades_manager)

    def process_event(self, id: int, event: CallEvent):
        print("Message Received " + event.message)

        for ca in event.contract_addresses:
            print("Received a call for https://solscan.io/token/" + ca) #can use ai to assess the sentiment

#Make sure the webhook server configured is running (I used ngrok to host localhost:5000 on my PC)
# Need a quick guide on setting up ngrok, ifttt, bluestacks, and discord channel; IFTTT has a twitter notis, but it's too slow
txdefitk = TxDefiToolKit()
social_media_tracker = SocialMediaListener(txdefitk.trades_manager)

txdefitk.trades_manager.run_strategy(social_media_tracker)


txdefitk.join() #Keep running until user shuts it down


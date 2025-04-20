import asyncio
import os
import sys

sys.path.insert(1, os.getcwd()) #needed to access resources outside this folder
from TxDefi.TxDefiToolKit import TxDefiToolKit
from TxDefi.UI.MainUi import MainUi

async def main():        
    program_executor = TxDefiToolKit()

    main_gui = MainUi(program_executor)
    main_gui.show_modal()

asyncio.run(main())
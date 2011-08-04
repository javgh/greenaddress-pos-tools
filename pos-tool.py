from controller import Controller
from greenaddresscheck.greenaddresscheck import GreenAddressCheck

controller = Controller()
green_address_check = GreenAddressCheck(controller.new_transaction_received)

green_address_check.start()
controller.run()

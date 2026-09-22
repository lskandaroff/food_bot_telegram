from aiogram.fsm.state import StatesGroup, State

class OrderFood(StatesGroup):
    ChoosingRestaurant = State()
    ChoosingMenu = State()
    ConfirmingOrder = State()
    WaitingForPhone = State()
    ChoosingDeliveryType = State()
    WaitingForLocation = State()
    ChoosingPaymentType = State()
    WaitingForReceipt = State()


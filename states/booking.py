from aiogram.fsm.state import State, StatesGroup


class BookingStates(StatesGroup):
    WAITING_NAME = State()
    WAITING_PHONE = State()
    WAITING_SERVICE = State()
    WAITING_DATE = State()
    WAITING_TIME = State()
    CONFIRM = State()


class CancelStates(StatesGroup):
    SELECT = State()
    CONFIRM = State()


class ReviewStates(StatesGroup):
    RATING = State()
    COMMENT = State()


class AdminStates(StatesGroup):
    PASSWORD = State()
    MENU = State()
    ADD_SERVICE_NAME = State()
    ADD_SERVICE_PRICE = State()
    REMOVE_SERVICE = State()

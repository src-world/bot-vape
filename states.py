from aiogram.fsm.state import State, StatesGroup

class PostState(StatesGroup):
    photo = State()
    name = State()
    price = State()
    flavors = State()
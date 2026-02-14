from aiogram import Router, types, F, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from config import ADMIN_ID, CHANNEL_ID
from states import PostState
import keyboards as kb

router = Router()

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    if message.from_user.id != ADMIN_ID: return
    await message.answer(
        "ПАНЕЛЬ УПРАВЛЕНИЯ\n________________________\n\nВыберите действие ниже:", 
        reply_markup=kb.kb_main()
    )

@router.message(F.text == "❌ Отмена")
async def cmd_cancel(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Создание отменено.", reply_markup=kb.kb_main())

@router.message(F.text == "📝 Создать новый пост")
async def start_creation(message: types.Message, state: FSMContext):
    await state.set_state(PostState.photo)
    await message.answer("ШАГ 1: ФОТО\nПришлите изображение товара:", reply_markup=types.ReplyKeyboardRemove())

@router.message(PostState.photo, F.photo)
async def process_photo(message: types.Message, state: FSMContext):
    await state.update_data(photo_id=message.photo[-1].file_id)
    await state.set_state(PostState.name)
    await message.answer("ШАГ 2: НАЗВАНИЕ\nВведите название:")

@router.message(PostState.name, F.text)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(PostState.price)
    await message.answer("ШАГ 3: ЦЕНА\nВведите стоимость:")

@router.message(PostState.price, F.text)
async def process_price(message: types.Message, state: FSMContext):
    await state.update_data(price=message.text, flavors=[])
    await state.set_state(PostState.flavors)
    await message.answer(
        "ШАГ 4: ВКУСЫ\nПишите вкусы по одному.\nКогда закончите — нажмите кнопку 'Готово'",
        reply_markup=kb.kb_flavors_finish()
    )

@router.message(PostState.flavors, F.text, F.text != "✅ Готово, предпросмотр")
async def add_flavor(message: types.Message, state: FSMContext):
    data = await state.get_data()
    flavors = data.get("flavors", [])
    flavors.append(message.text)
    await state.update_data(flavors=flavors)
    await message.answer(f"• {message.text} добавлен")

@router.message(PostState.flavors, F.text == "✅ Готово, предпросмотр")
async def finish_post(message: types.Message, state: FSMContext):
    data = await state.get_data()
    if not data.get('flavors'):
        return await message.answer("Добавьте хотя бы один вкус!")

    flavors_list = "\n\n".join([f"{f} — ✅" for f in data['flavors']])
    caption = (
        f"{data['name']}\n\n"
        f"Цена: {data['price']}\n\n"
        f"Вкусы:\n\n"
        f"{flavors_list}\n"
        f"________________________\n\n"
        f"Приобрести у него: @Den_41_ka\n\n"
        f"Вкусы могут обновляться и добавляться новые."
    )
    
    await state.update_data(final_caption=caption)
    await message.answer("ПРЕДПРОСМОТР:", reply_markup=kb.kb_main())
    await message.answer_photo(photo=data['photo_id'], caption=caption)
    await message.answer("Все верно?", reply_markup=kb.kb_preview_inline())

@router.callback_query(F.data == "publish")
async def publish_final(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    try:
        sent = await bot.send_photo(
            chat_id=CHANNEL_ID,
            photo=data['photo_id'],
            caption=data['final_caption']
        )
        await callback.message.edit_text("✅ Опубликовано!", reply_markup=kb.kb_del_post(sent.message_id))
    except Exception as e:
        await callback.message.answer(f"Ошибка: {e}")
    await state.clear()

@router.callback_query(F.data == "reset")
async def reset_post(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("Черновик удален.")

@router.callback_query(F.data.startswith("drop_"))
async def drop_post(callback: types.CallbackQuery, bot: Bot):
    msg_id = int(callback.data.split("_")[1])
    try:
        await bot.delete_message(chat_id=CHANNEL_ID, message_id=msg_id)
        await callback.message.edit_text("🗑 Пост удален.")
    except:
        await callback.answer("Не удалось удалить пост.")
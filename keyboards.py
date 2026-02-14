from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram import types

def kb_main():
    builder = ReplyKeyboardBuilder()
    builder.button(text="📝 Создать новый пост")
    return builder.as_markup(resize_keyboard=True)

def kb_flavors_finish():
    builder = ReplyKeyboardBuilder()
    builder.button(text="✅ Готово, предпросмотр")
    builder.button(text="❌ Отмена")
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)

def kb_preview_inline():
    builder = InlineKeyboardBuilder()
    builder.button(text="🚀 ОПУБЛИКОВАТЬ", callback_data="publish")
    builder.button(text="🔄 СБРОСИТЬ", callback_data="reset")
    builder.adjust(1)
    return builder.as_markup()

def kb_del_post(message_id):
    builder = InlineKeyboardBuilder()
    builder.button(text="🗑 Удалить из канала", callback_data=f"drop_{message_id}")
    return builder.as_markup()
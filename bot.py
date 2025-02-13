import logging
import requests
import asyncio
import os
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
API_URL = os.getenv("API_URL")
admin_ids_env = os.getenv("ADMIN_IDS", "")
ADMIN_IDS = [x.strip() for x in admin_ids_env.split(",") if x.strip()]

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())
logging.basicConfig(level=logging.INFO)


def is_admin(telegram_id):
    return str(telegram_id) in ADMIN_IDS

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="➕ Create Task"), KeyboardButton(text="📋 List Tasks")],
        [KeyboardButton(text="🔍 Get Task by ID"), KeyboardButton(text="✏️ Update Task")],
        [KeyboardButton(text="❌ Delete Task"), KeyboardButton(text="🗑 Delete All Tasks")],
        [KeyboardButton(text="➕ Add User"), KeyboardButton(text="❌ Delete User")],
        [KeyboardButton(text="✏️ Edit User"), KeyboardButton(text="🔎 Search Domains")],
        [KeyboardButton(text="📋 Get All Users")]
    ],
    resize_keyboard=True
)

class CreateTask(StatesGroup):
    waiting_description = State()

class GetTask(StatesGroup):
    waiting_id = State()

class UpdateTask(StatesGroup):
    waiting_update = State()

class DeleteTask(StatesGroup):
    waiting_id = State()

class AdminAddUser(StatesGroup):
    waiting_info = State()

class AdminDeleteUser(StatesGroup):
    waiting_telegram_id = State()

class AdminEditUser(StatesGroup):
    waiting_info = State()

class DomainSearch(StatesGroup):
    waiting_domains = State()


@dp.message(Command("start"))
async def cmd_start(message: Message):
    """Send the welcome message and display the main menu."""
    await message.answer("Hello! I'm your ToDo Bot.\nChoose an action below:", reply_markup=main_menu)


@dp.message(F.text == "➕ Create Task")
async def cmd_create_task(message: Message, state: FSMContext):
    """Prompt the user to enter a task description."""
    await message.answer("Please send the task description:")
    await state.set_state(CreateTask.waiting_description)


@dp.message(CreateTask.waiting_description, F.text)
async def process_create_task(message: Message, state: FSMContext):
    """Receive task description, send it to the Flask API, and exit the state."""
    data = {"description": message.text}
    response = requests.post(f"{API_URL}/create-todo", json=data)
    if response.status_code == 201:
        await message.answer("✅ Task created successfully!", reply_markup=main_menu)
    else:
        await message.answer("⚠️ Failed to create task.", reply_markup=main_menu)
    await state.clear()


@dp.message(F.text == "📋 List Tasks")
async def cmd_list_tasks(message: Message):
    """Retrieve and display all tasks from the database."""
    response = requests.get(f"{API_URL}/get-all-todo")
    if response.status_code == 200:
        todos = response.json().get("todos", [])
        if not todos:
            await message.answer("ℹ️ No tasks available.", reply_markup=main_menu)
        else:
            text = "\n".join([f"🆔 {todo['id']}: {todo['description']}" for todo in todos])
            await message.answer(f"📋 Task List:\n{text}", reply_markup=main_menu)
    else:
        await message.answer("⚠️ Failed to retrieve tasks.", reply_markup=main_menu)


@dp.message(F.text == "🔍 Get Task by ID")
async def cmd_get_task(message: Message, state: FSMContext):
    """Prompt the user to enter a task ID."""
    await message.answer("Please send the task ID:")
    await state.set_state(GetTask.waiting_id)


@dp.message(GetTask.waiting_id, F.text)
async def process_get_task(message: Message, state: FSMContext):
    """Retrieve and display a specific task by ID."""
    todo_id = message.text.strip()
    if not todo_id.isdigit():
        await message.answer("⚠️ Please enter a valid number.")
        return
    response = requests.get(f"{API_URL}/get-todo?id={todo_id}")
    if response.status_code == 200:
        todo = response.json().get("todo", {})
        text = f"📌 Task:\nID: {todo.get('id')}\nDescription: {todo.get('description')}\nCreated: {todo.get('created_at')}"
        await message.answer(text, reply_markup=main_menu)
    else:
        await message.answer("⚠️ Task not found.", reply_markup=main_menu)
    await state.clear()


@dp.message(F.text == "✏️ Update Task")
async def cmd_update_task(message: Message, state: FSMContext):
    """Prompt the user to enter task ID and new description."""
    await message.answer("Send `ID; New description` (e.g., `1; Updated task`):")
    await state.set_state(UpdateTask.waiting_update)


@dp.message(UpdateTask.waiting_update, F.text)
async def process_update_task(message: Message, state: FSMContext):
    """Update a task using provided ID and new description."""
    if ";" not in message.text:
        await message.answer("⚠️ Incorrect format. Use `ID; New description`.", reply_markup=main_menu)
        await state.clear()
        return
    try:
        todo_id, new_description = message.text.split(";")
        data = {"id": todo_id.strip(), "description": new_description.strip()}
        response = requests.put(f"{API_URL}/update-todo", json=data)
        if response.status_code == 200:
            await message.answer("✅ Task updated successfully!", reply_markup=main_menu)
        else:
            await message.answer("⚠️ Failed to update task.", reply_markup=main_menu)
    except ValueError:
        await message.answer("⚠️ Incorrect format. Use `ID; New description`.", reply_markup=main_menu)
    await state.clear()


@dp.message(F.text == "❌ Delete Task")
async def cmd_delete_task(message: Message, state: FSMContext):
    """Prompt the user to enter a task ID for deletion."""
    await message.answer("Please send the task ID to delete:")
    await state.set_state(DeleteTask.waiting_id)


@dp.message(DeleteTask.waiting_id, F.text)
async def process_delete_task(message: Message, state: FSMContext):
    """Delete a task by ID."""
    todo_id = message.text.strip()
    if not todo_id.isdigit():
        await message.answer("⚠️ Please enter a valid number.", reply_markup=main_menu)
        await state.clear()
        return
    data = {"id": todo_id}
    response = requests.delete(f"{API_URL}/delete-todo", json=data)
    if response.status_code == 200:
        await message.answer("✅ Task deleted successfully!", reply_markup=main_menu)
    else:
        await message.answer("⚠️ Failed to delete task.", reply_markup=main_menu)
    await state.clear()


@dp.message(F.text.lower() == "🗑 delete all tasks")
async def cmd_delete_all_tasks(message: Message):
    """Delete all tasks from the database."""
    response = requests.delete(f"{API_URL}/delete-all-todo")
    if response.status_code == 200:
        deleted_count = response.json().get("message", "Unknown response")
        await message.answer(f"✅ {deleted_count}", reply_markup=main_menu)
    else:
        await message.answer("⚠️ Failed to delete all tasks.", reply_markup=main_menu)


@dp.message(F.text == "📋 Get All Users")
async def cmd_get_all_users(message: Message):
    """Retrieve and display all users (admin only)."""
    if not is_admin(message.from_user.id):
        await message.answer("Access denied.", reply_markup=main_menu)
        return
    response = requests.get(f"{API_URL}/get-users")
    if response.status_code == 200:
        users = response.json().get("users", [])
        if not users:
            await message.answer("ℹ️ No users available.", reply_markup=main_menu)
        else:
            text = "\n".join([f"👤 {user['telegram_id']} ({user['group']})" for user in users])
            await message.answer(f"📋 Users:\n{text}", reply_markup=main_menu)
    else:
        await message.answer("⚠️ Failed to retrieve users.", reply_markup=main_menu)


@dp.message(F.text == "➕ Add User")
async def cmd_add_user(message: Message, state: FSMContext):
    """Prompt the admin to enter Telegram ID and group to add a user."""
    if not is_admin(message.from_user.id):
        await message.answer("Access denied.", reply_markup=main_menu)
        return
    await message.answer("Enter user info in format: telegram_id, group (e.g., 123456789, test_user):")
    await state.set_state(AdminAddUser.waiting_info)


@dp.message(AdminAddUser.waiting_info, F.text)
async def process_add_user(message: Message, state: FSMContext):
    """Add a user using the provided info."""
    if not is_admin(message.from_user.id):
        await message.answer("Access denied.", reply_markup=main_menu)
        await state.clear()
        return
    try:
        telegram_id, group = [x.strip() for x in message.text.split(",")]
        data = {"telegram_id": telegram_id, "group": group}
        response = requests.post(f"{API_URL}/add-user", json=data)
        if response.status_code == 201:
            await message.answer("✅ User added successfully.", reply_markup=main_menu)
        else:
            await message.answer("⚠️ Failed to add user.", reply_markup=main_menu)
    except Exception:
        await message.answer("⚠️ Incorrect format. Use: telegram_id, group", reply_markup=main_menu)
    await state.clear()


@dp.message(F.text == "❌ Delete User")
async def cmd_delete_user(message: Message, state: FSMContext):
    """Prompt the admin to enter Telegram ID to delete a user."""
    if not is_admin(message.from_user.id):
        await message.answer("Access denied.", reply_markup=main_menu)
        return
    await message.answer("Enter the Telegram ID of the user to delete:")
    await state.set_state(AdminDeleteUser.waiting_telegram_id)


@dp.message(AdminDeleteUser.waiting_telegram_id, F.text)
async def process_delete_user(message: Message, state: FSMContext):
    """Delete a user with the provided Telegram ID."""
    if not is_admin(message.from_user.id):
        await message.answer("Access denied.", reply_markup=main_menu)
        await state.clear()
        return
    telegram_id = message.text.strip()
    data = {"telegram_id": telegram_id}
    response = requests.delete(f"{API_URL}/delete-user", json=data)
    if response.status_code == 200:
        await message.answer("✅ User deleted successfully.", reply_markup=main_menu)
    else:
        await message.answer("⚠️ Failed to delete user.", reply_markup=main_menu)
    await state.clear()


@dp.message(F.text == "✏️ Edit User")
async def cmd_edit_user(message: Message, state: FSMContext):
    """Prompt the admin to enter Telegram ID and new group to update a user."""
    if not is_admin(message.from_user.id):
        await message.answer("Access denied.", reply_markup=main_menu)
        return
    await message.answer("Enter user info in format: telegram_id, new group (e.g., 123456789, admin):")
    await state.set_state(AdminEditUser.waiting_info)


@dp.message(AdminEditUser.waiting_info, F.text)
async def process_edit_user(message: Message, state: FSMContext):
    """Update a user's group using the provided info."""
    if not is_admin(message.from_user.id):
        await message.answer("Access denied.", reply_markup=main_menu)
        await state.clear()
        return
    try:
        telegram_id, new_group = [x.strip() for x in message.text.split(",")]
        data = {"telegram_id": telegram_id, "group": new_group}
        response = requests.put(f"{API_URL}/edit-user", json=data)
        if response.status_code == 200:
            await message.answer("✅ User updated successfully.", reply_markup=main_menu)
        else:
            await message.answer("⚠️ Failed to update user.", reply_markup=main_menu)
    except Exception:
        await message.answer("⚠️ Incorrect format. Use: telegram_id, new group", reply_markup=main_menu)
    await state.clear()


@dp.message(F.text == "🔎 Search Domains")
async def cmd_search_domains(message: Message, state: FSMContext):
    """Prompt the user to enter a list of domains for checking."""
    await message.answer("Enter domains (each on a new line):")
    await state.set_state(DomainSearch.waiting_domains)


@dp.message(DomainSearch.waiting_domains, F.text)
async def process_search_domains(message: Message, state: FSMContext):
    """Send the list of domains to the Flask API and display the results."""
    data = {"domains": message.text}
    response = requests.post(f"{API_URL}/search-domains", json=data)
    if response.status_code == 200:
        results = response.json().get("results", [])
        reply = ""
        for res in results:
            reply += (f"Domain: {res.get('domain')}\n"
                      f"- SSL: {res.get('ssl')}\n"
                      f"- Status: {res.get('status')}\n"
                      f"- Availability: {res.get('availability')}\n\n")
        await message.answer(reply.strip(), reply_markup=main_menu)
    else:
        await message.answer("⚠️ Failed to check domains.", reply_markup=main_menu)
    await state.clear()


async def main():
    """Run the bot and start polling updates."""
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())

import aiogram
import sqlite3
from aiogram.contrib.fsm_storage.memory import MemoryStorage

bot = aiogram.Bot(token='6077389191:AAHv-_ngFjHTeavbiXsaCGgcN-WCiC1YqK8')
storage = MemoryStorage()
dp = aiogram.Dispatcher(bot, storage=storage)

con = sqlite3.connect("db.sqlite3")
cur = con.cursor()
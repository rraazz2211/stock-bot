# ייבוא הספריות שהתקנו
import discord
from discord.ext import commands, tasks
import yfinance as yf
import os
from dotenv import load_dotenv
import asyncio
from datetime import time

# טוען את הקובץ .env (הסודות שלנו)
load_dotenv()

# לוקח את ה-TOKEN מהקובץ .env
TOKEN = os.getenv('DISCORD_TOKEN')

# יוצר את הבוט
bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())

# משתנה גלובלי לשמור את המשתמש האחרון
last_user = None

@tasks.loop(time=time(hour=11, minute=0))  # כל יום ב-11:00 בבוקר!
async def daily_reminder():

    
    global last_user
    if last_user:
        print(f"📱 שולח DM למשתמש: {last_user.name}")
        try:
            await last_user.send('🔔 היי! זמן ללמוד תכנות! 💻📊\nבוא נמשיך לבנות את הבוט! 🚀')
            print("✅ הודעה פרטית נשלחה בהצלחה!")
        except discord.Forbidden:
            print("❌ המשתמש חסם הודעות פרטיות מהבוט")
        except Exception as e:
            print(f"❌ שגיאה בשליחת DM: {e}")
    else:
        print("❌ אין משתמש רשום - כתוב !ping כדי להירשם לתזכורות")

# שומר את המשתמש האחרון שדיבר עם הבוט
@bot.event
async def on_message(message):
    global last_user
    # שומר את המשתמש האחרון שהשתמש בפקודה (ולא את הבוט עצמו)
    if message.content.startswith('!') and not message.author.bot:
        last_user = message.author
        print(f"✅ נרשם משתמש לתזכורות: {message.author.name}")
    
    # חשוב! זה מאפשר לפקודות לעבוד
    await bot.process_commands(message)

# פונקציה שרצה כשהבוט מתחבר בהצלחה
@bot.event
async def on_ready():
    print(f'{bot.user} התחבר בהצלחה!')
    print('הבוט מוכן לעבודה! 🚀')
    daily_reminder.start()  # מפעיל את התזכורת היומית

# פקודה פשוטה לבדיקה
@bot.command()
async def ping(ctx):
    await ctx.send('Pong! 🏓\n✅ נרשמת לקבלת תזכורות יומיות!')

# פקודה למשיכת מחיר מניה
@bot.command()
async def price(ctx, ticker: str):
    print(f"📊 מישהו ביקש מחיר של: {ticker}")
    
    await ctx.send(f"🔍 מחפש מידע על {ticker.upper()}...")
    
    try:
        stock = yf.Ticker(ticker.upper())
        print(f"✅ יצרתי חיבור למניה")
        
        info = stock.info
        print(f"✅ קיבלתי מידע")
        
        if 'regularMarketPrice' in info:
            current_price = info['regularMarketPrice']
        elif 'currentPrice' in info:
            current_price = info['currentPrice']
        else:
            await ctx.send(f"❌ לא מצאתי מחיר עבור {ticker.upper()}")
            return
        
        print(f"✅ מצאתי מחיר: ${current_price}")
        
        await ctx.send(f'💰 {ticker.upper()}: ${current_price}')
    
    except Exception as e:
        print(f"❌ שגיאה: {e}")
        await ctx.send(f'❌ לא הצלחתי למצוא מידע על {ticker}')

# פקודת hello
@bot.command()
async def hello(ctx):
    await ctx.send(f'Hi asshole {ctx.author.mention}!')

# תזכורת חד-פעמית
@bot.command()
async def remindme(ctx, minutes: int, *, message: str):
    """
    שליחת תזכורת אחרי X דקות
    שימוש: !remindme 30 ללמוד תכנות
    """
    await ctx.send(f'⏰ אזכיר לך בעוד {minutes} דקות!')
    
    # המתנה
    await asyncio.sleep(minutes * 60)
    
    # שליחת התזכורת כ-DM
    try:
        await ctx.author.send(f'🔔 תזכורת: {message}')
    except discord.Forbidden:
        await ctx.send(f'{ctx.author.mention} 🔔 תזכורת: {message}')

# מריץ את הבוט עם ה-TOKEN
bot.run(TOKEN)
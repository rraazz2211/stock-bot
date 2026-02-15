# ייבוא הספריות שהתקנו
import discord
from discord.ext import commands, tasks
import yfinance as yf
import os
from dotenv import load_dotenv
import asyncio
from datetime import time
import matplotlib.pyplot as plt

# טוען את הקובץ .env (הסודות שלנו)
load_dotenv()

# לוקח את ה-TOKEN מהקובץ .env
TOKEN = os.getenv('DISCORD_TOKEN')

# יוצר את הבוט
bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())

# משתנה גלובלי לשמור את המשתמש האחרון
last_user = None

# תזכורת יומית
@tasks.loop(time=time(hour=11, minute=0))
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
    if message.content.startswith('!') and not message.author.bot:
        last_user = message.author
        print(f"✅ נרשם משתמש לתזכורות: {message.author.name}")
    
    await bot.process_commands(message)

# פונקציה שרצה כשהבוט מתחבר בהצלחה
@bot.event
async def on_ready():
    print(f'{bot.user} התחבר בהצלחה!')
    print('הבוט מוכן לעבודה! 🚀')
    daily_reminder.start()

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
    
    await asyncio.sleep(minutes * 60)
    
    try:
        await ctx.author.send(f'🔔 תזכורת: {message}')
    except discord.Forbidden:
        await ctx.send(f'{ctx.author.mention} 🔔 תזכורת: {message}')

# ===============================
# פקודת ניתוח מתקדמת! ⭐
# ===============================

@bot.command()
async def analyze(ctx, symbol: str):
    """
    ניתוח מתקדם של מניה
    שימוש: !analyze AAPL
    """
    symbol = symbol.upper()
    
    await ctx.send(f"🔍 מנתח {symbol}... רגע אחד...")
    
    try:
        # משיכת נתונים
        stock = yf.Ticker(symbol)
        df = stock.history(period="90d")
        
        print(f"נמשכו {len(df)} שורות")
        
        if len(df) == 0:
            await ctx.send(f"❌ לא מצאתי נתונים עבור {symbol}")
            return
        
        # חישובים
        df['SMA_20'] = df['Close'].rolling(window=20).mean()
        df['SMA_50'] = df['Close'].rolling(window=50).mean()
        
        # RSI
        delta = df['Close'].diff()
        gain = delta.where(delta > 0, 0).rolling(window=14).mean()
        loss = -delta.where(delta < 0, 0).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        df = df.dropna()
        
        if df.index.tz is not None:
            df.index = df.index.tz_localize(None)
        
        print(f"אחרי dropna: {len(df)} שורות")
        
        if len(df) == 0:
            await ctx.send(f"❌ לא מספיק נתונים לניתוח {symbol}")
            return
        
        # נתונים אחרונים
        last_row = df.iloc[-1]
        current_price = float(last_row['Close'])
        current_rsi = float(last_row['RSI'])
        sma_20 = float(last_row['SMA_20'])
        sma_50 = float(last_row['SMA_50'])
        
        # שינוי
        first_price = float(df.iloc[0]['Close'])
        change_pct = ((current_price / first_price) - 1) * 100
        
        # מגמה
        if current_price > sma_20 > sma_50:
            trend = "📈 Strong Uptrend"
        elif current_price > sma_20:
            trend = "📈 Uptrend"
        elif current_price < sma_20 < sma_50:
            trend = "📉 Strong Downtrend"
        elif current_price < sma_20:
            trend = "📉 Downtrend"
        else:
            trend = "➡️ Sideways"
        
        # אות RSI
        if current_rsi < 30:
            signal = "🟢 BUY - Oversold"
        elif current_rsi > 70:
            signal = "🔴 SELL - Overbought"
        else:
            signal = "🟡 HOLD - Normal range"
        
        # הודעה
        message = f"""**📊 Analysis: {symbol}**

💰 **Price:** ${current_price:.2f}
📈 **Change (90d):** {change_pct:+.2f}%
🎯 **RSI:** {current_rsi:.1f}
📉 **MA 20:** ${sma_20:.2f}
📉 **MA 50:** ${sma_50:.2f}

**Trend:** {trend}
**Signal:** {signal}"""
        
        await ctx.send(message)
        
        # גרף
        await ctx.send("🎨 Creating chart...")
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
        
        ax1.plot(df.index, df['Close'], 'k-', linewidth=2, label='Price')
        ax1.plot(df.index, df['SMA_20'], 'b-', linewidth=1.5, alpha=0.7, label='MA 20')
        ax1.plot(df.index, df['SMA_50'], 'r-', linewidth=1.5, alpha=0.7, label='MA 50')
        ax1.set_title(f'{symbol} - Price & Moving Averages', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Price ($)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        ax2.plot(df.index, df['RSI'], 'purple', linewidth=2)
        ax2.axhline(70, color='red', linestyle='--', linewidth=1)
        ax2.axhline(30, color='green', linestyle='--', linewidth=1)
        ax2.fill_between(df.index, 30, 70, alpha=0.1, color='gray')
        ax2.set_title('RSI', fontsize=12, fontweight='bold')
        ax2.set_ylabel('RSI')
        ax2.set_xlabel('Date')
        ax2.set_ylim(0, 100)
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        filename = f"{symbol}_analysis.png"
        plt.savefig(filename, dpi=200, bbox_inches='tight')
        plt.close()
        
        await ctx.send(file=discord.File(filename))
        
        os.remove(filename)
        
        print(f"✅ ניתוח {symbol} הושלם")
        
    except Exception as e:
        print(f"❌ שגיאה: {e}")
        await ctx.send(f"❌ שגיאה: {str(e)}")

# מריץ את הבוט עם ה-TOKEN
bot.run(TOKEN)
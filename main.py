import telebot
from googletrans import Translator, LANGUAGES
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from telebot import types
import time
from datetime import datetime, timedelta
from selenium.common.exceptions import NoSuchElementException


from bs4 import BeautifulSoup
import requests
# ضع رمز البوت الخاص بك هنا
BOT_TOKEN = '7287074566:AAEJjZLSFiTcr4exaQQKDPRkq1XRsPshBqU'
CHANNEL_USERNAME = '@osm23_24'  # ضع اسم القناة هنا
ADMIN_ID = 970547416  # ضع معرف المستخدم الخاص بك كمالك البوت
PRINUM_USERS = [588461026, 970547416]

bot = telebot.TeleBot(BOT_TOKEN)

# بيانات المستخدم
user_data = {}

# قائمة اللغات المدعومة
languages = {
    'ar': 'العربية',
    'en': 'English',
    'tr': 'Tukish'
}
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--remote-debugging-port=9222")

chrome_options.add_argument("--window-size=1920, 1080")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--disable-notifications")
chrome_options.add_argument("--disable-advertisement")
chrome_options.add_argument("--disable-popup-blocking")
    
driver = webdriver.Chrome(options=chrome_options)
time.sleep(3)
# ... التحقق من الاشتراك في القناة
def check_subscription(user_id):
    try:
        member_status = bot.get_chat_member(CHANNEL_USERNAME, user_id).status
        return member_status in ['member', 'administrator', 'creator']
    except Exception as e:
        print(f"Error checking subscription...")
        return False

#  إرسال رسالة الاشتراك الإجباري
def send_subscription_message(chat_id):
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton(text='اشترك في القناة اولا', url=f'https://t.me/{CHANNEL_USERNAME.strip("@")}')
    markup.add(btn)
    bot.send_message(chat_id, 'يرجى الاشتراك في القناة لاستخدام البوت.', reply_markup=markup)

# دالة البداية
@bot.message_handler(commands=['start'])
def send_welcome(message):
    if not check_subscription(message.from_user.id):
        send_subscription_message(message.chat.id)
        return

    '''markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    for code, lang in languages.items():
        markup.add(types.KeyboardButton(lang))'''
    
    bot.send_message(message.chat.id, "مرحباً! بك في بوت تحليل خصمك ومعرفة جميع تفاصيل خطته، بالاضافة الي اشعارك بنتائج المباريات اضغط على /login لتسجيل الدخول الى حسابك في OSM:" )#reply_markup=markup)
    #bot.register_next_step_handler(message, set_language)


'''def set_language(message):
    chat_id = message.chat.id
    for code, lang in languages.items():
        if message.text == lang:
            user_data[chat_id] = {'language': code}
            bot.send_message(chat_id, f"تم اختيار اللغة: {lang}")
            bot.send_message(message.chat.id, "مرحباً! بك في بوت تحليل خصمك ومعرفة جميع تفاصيل خطته، بالاضافة الي اشعارك بنتائج المباريات اضغط على /login لتسجيل الدخول الى حسابك في OSM:")
            show_main_menu(chat_id)
            return
    bot.send_message(chat_id, "يرجى اختيار لغة صالحة.")
    bot.register_next_step_handler(message, set_language)'''

# دالة تسجيل الدخول
@bot.message_handler(commands=['login'])
def ask_username(message):
    bot.send_message(message.chat.id, "يرجى إدخال اسم المستخدم في OSM:")
    bot.register_next_step_handler(message, get_username)

def get_username(message):
    chat_id = message.chat.id
    user_data[chat_id] = {'username': message.text}
    bot.send_message(chat_id, "يرجى إدخال كلمة المرور:")
    bot.register_next_step_handler(message, get_password)

def get_password(message):
    chat_id = message.chat.id
    user_data[chat_id]['password'] = message.text
    login_success = osm_login(user_data[chat_id]['username'], user_data[chat_id]['password'])
    

    
    if login_success:
        bot.send_message(chat_id, " تم تسجيل الدخول بنجاح! يمكنك الآن التفاعل مع حسابك بواسطة الازرار ادناه.")
        show_main_menu(chat_id)
        
    else:
        bot.send_message(chat_id, "فشل تسجيل الدخول. حاول مرة أخرى باستخدام الأمر /login.")

def osm_login(username, password):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--window-size=1920, 1080")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--disable-advertisement")
    chrome_options.add_argument("--disable-popup-blocking")
    
    global driver
    driver = webdriver.Chrome(options=chrome_options)
    
    driver.get("https://ar.onlinesoccermanager.com/Login")
    time.sleep(3)

    try:
        button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "btn-orange"))
        )
        button.click()
    except:
        print("Button not found using")

    driver.get("https://ar.onlinesoccermanager.com/Login")
    
    time.sleep(3)
    # الانتظار حتى يظهر الحقلين
       
    # Locate the username input field
    username_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "manager-name"))
    )

    # Locate the password input field
    password_field = driver.find_element(By.ID, "password")

    # Locate the login button
    login_button = driver.find_element(By.ID, "login")

    # Enter username and password
    username_field.send_keys(username)
    password_field.send_keys(password)

    # Click the login button to submit the form
    login_button.click()
    time.sleep(5)
    driver.get('https://ar.onlinesoccermanager.com/Career?nextUrl=/Login')
    '''global html_con
    html_con = driver.find_element(By.CLASS_NAME, 'row-h-xs-24')'''

    WebDriverWait(driver, 10).until(EC.url_contains('Career'))
    print(driver.current_url)
    global main_url
    main_url = driver.current_url
    
    
    if 'Career' in main_url:
       

        return True
    else:
        return False
# دالة عرض القائمة الرئيسية
def show_main_menu(chat_id):
    
    driver.get('https://ar.onlinesoccermanager.com/Career?nextUrl=/Login') 
    time.sleep(3)  
    # التعريف بمواقع العناصر باستخدام XPath
    matchday = [
        '//*[@id="body-content"]/div[2]/div[1]/div/div[1]/div/div[2]/div/div[2]/div[2]/div/div/span',
        '//*[@id="body-content"]/div[2]/div[1]/div/div[2]/div/div[2]/div/div[2]/div[2]/div/div/span',
        '//*[@id="body-content"]/div[2]/div[1]/div/div[3]/div/div[2]/div/div[2]/div[2]/div/div/span',
        '//*[@id="body-content"]/div[2]/div[1]/div/div[4]/div/div[2]/div/div[2]/div[2]/div/div/span'
    ]

    club = [
        '//*[@id="body-content"]/div[2]/div[1]/div/div[1]/div/div[2]/div/div[3]/div/div/div[2]/div/div/h2',
        '//*[@id="body-content"]/div[2]/div[1]/div/div[2]/div/div[2]/div/div[3]/div/div/div[2]/div/div/h2',
        '//*[@id="body-content"]/div[2]/div[1]/div/div[3]/div/div[2]/div/div[3]/div/div/div[2]/div/div/h2',
        '//*[@id="body-content"]/div[2]/div[1]/div/div[4]/div/div[2]/div/div[3]/div/div/div[2]/div/div/h2'
    ]

    league = [
        '//*[@id="body-content"]/div[2]/div[1]/div/div[1]/div/div[2]/div/div[3]/div/div/div[2]/div/div/h4',
        '//*[@id="body-content"]/div[2]/div[1]/div/div[2]/div/div[2]/div/div[3]/div/div/div[2]/div/div/h4',
        '//*[@id="body-content"]/div[2]/div[1]/div/div[3]/div/div[2]/div/div[3]/div/div/div[2]/div/div/h4',
        '//*[@id="body-content"]/div[2]/div[1]/div/div[4]/div/div[2]/div/div[3]/div/div/div[2]/div/div/h4'
    ]

    matchday_lst = []
    club_lst = []
    league_lst = []

    for i in range(4):
        try:
            m = driver.find_element(By.XPATH, matchday[i])
            c = driver.find_element(By.XPATH, club[i])
            l = driver.find_element(By.XPATH, league[i])
            if not (m and c and l):
                matchday_lst.append('?')
                club_lst.append('?')
                league_lst.append('___')


            else:
                matchday_lst.append(m.text)
                club_lst.append(c.text)
                league_lst.append(l.text)
        except Exception as e:
            print(f"Error occurred at index {i}: {str(e)}")
            matchday_lst.append('?')
            club_lst.append('?')
            league_lst.append('___')
            pass

    # طباعة القيم المستخرجة
    print("Matchdays:", matchday_lst)
    print("Clubs:", club_lst)
    print("Leagues:", league_lst)
    try:

        global button1, button2, button3, button4
        button1 = '{} -> {} ({})'.format(club_lst[0], league_lst[0], matchday_lst[0])
        button2 = '{} -> {} ({})'.format(club_lst[1], league_lst[1], matchday_lst[1])
        button3 = '{} -> {} ({})'.format(club_lst[2], league_lst[2], matchday_lst[2])
        button4 = '{} -> {} ({})'.format(club_lst[3], league_lst[3], matchday_lst[3])
    except:
        pass


    
    # Creating a ReplyKeyboardMarkup object
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)

    # Generating buttons with text
    btn1 = types.KeyboardButton(button1)

    if chat_id not in PRINUM_USERS:
        btn2 = types.KeyboardButton('فقط باشتراك مدفوع ')
        btn3 = types.KeyboardButton('فقط باشتراك مدفوع')
        btn4 = types.KeyboardButton('فقط باشتراك مدفوع')
    else:
        btn2 = types.KeyboardButton(button2)
        btn3 = types.KeyboardButton(button3)
        btn4 = types.KeyboardButton(button4)

    btn5 = types.KeyboardButton('النتائج')
    btn6 = types.KeyboardButton('الجولة القادمة')
    btn7 = types.KeyboardButton('تسجيل خروج')
    btn8 = types.KeyboardButton('رجوع')
    btn9 = types.KeyboardButton('مساعدة')
    # Adding buttons to markup
    markup.add(btn1, btn2, btn3, btn4, btn5, btn6, btn7, btn8, btn9)

    # Sending the message with options
    bot.send_message(chat_id, "اختر أحد الخيارات:", reply_markup=markup)

    

    @bot.message_handler(func=lambda message: True)
    def handle_buttons(message):
        try:
            if message.text == button1:
                element = driver.find_element(By.XPATH, '//*[@id="body-content"]/div[2]/div[1]/div/div[1]/div/div[2]/div')
                element.click()
                time.sleep(2)
                
                bot.send_message(message.chat.id, data_analysis())

            elif message.text == button2:
                element = driver.find_element(By.XPATH, '//*[@id="body-content"]/div[2]/div[1]/div/div[2]/div/div[2]/div')
                element.click()
                time.sleep(2)
                bot.send_message(message.chat.id, data_analysis())

            elif message.text == button3:
                element = driver.find_element(By.XPATH, '//*[@id="body-content"]/div[2]/div[1]/div/div[3]/div/div[2]/div')
                element.click()
                time.sleep(2)
                bot.send_message(message.chat.id, data_analysis())

            elif message.text == button4:
                element = driver.find_element(By.XPATH, '//*[@id="body-content"]/div[2]/div[1]/div/div[4]/div/div[2]/div')
                element.click()
                time.sleep(2)
                bot.send_message(message.chat.id, data_analysis())

            elif message.text == 'النتائج':
                driver.get('https://ar.onlinesoccermanager.com/League/Results')
                time.sleep(2)
                # استرجاع العناصر من الصفحة
                table_data = get_results()
                bot.send_message(message.chat.id, table_data)

            elif message.text == 'الجولة القادمة':
                driver.get('https://ar.onlinesoccermanager.com/League/Fixtures')
                time.sleep(2)
                # استرجاع العناصر من الصفحة
                table_data = extract_fixtures_data()
                bot.send_message(message.chat.id, table_data)

            elif message.text == 'تسجيل خروج':
                osm_logout()
                time.sleep(2)
                bot.send_message(chat_id, 'تم تسجيل الخروج')
            elif message.text == 'رجوع':
                driver.get('https://ar.onlinesoccermanager.com/Career?nextUrl=/Login')
                time.sleep(2)
                bot.send_message(chat_id, 'تمت العودة للقائمة الرئيسية اختر احد الخانات')
                
            elif message.text == 'مساعدة':
                help_text = (
                        '''لاستخدام هذا الروبوت، اتبع الخطوات التالية:

                1. قم بتسجيل الدخول إلى حسابك باستخدام اسمك باللعبة وكلمة المرور.
                2. بعد تسجيل الدخول، اختر فتحة فريقك لعرض نتائج التجسس.
                3. يرجى التأكد من أنك قمت بإرسال محلل البيانات مسبقًا وقمت بفتح النتائج المرتجعة لرؤية معلومات إضافية.

                🚨 هذا البوت يتبع بوت المدرب الأفضل ويشرف عليه ساكو @sako7osm

                🛍 لشحن الكوينز و ملايين المدرب الأفضل ادخل المتجر واختار باقتك بعنايه : t.me/Dani5zzbot
                للتعليق على مشاكل البوت - مطور البوت: @hemonybot
                '''
                        
                        # Add more commands as needed
                    )
                bot.send_message(chat_id, help_text)
            else:
                bot.send_message(message.chat.id, "يرجى اختيار خيار صحيح من القائمة.")
        except Exception as e:
            bot.send_message(message.chat.id, f"حدث خطأ: ")

def get_results():
    driver.get('https://ar.onlinesoccermanager.com/League/Results')
    time.sleep(2)
    try:
        hed1 = driver.find_element(By.XPATH, '//*[@id="fixtures-list"]/div/div/table/thead/tr/th[1]/span').text
        hed2 = driver.find_element(By.XPATH, '//*[@id="fixtures-list"]/div/div/table/thead/tr/th[2]/span').text
        hed3 = driver.find_element(By.XPATH, '//*[@id="fixtures-list"]/div/div/table/thead/tr/th[3]/span').text

        rows = []
        for i in range(2, 11):  # Assuming there are 9 rows to scrape
            try:
                row_data = [
                    driver.find_element(By.XPATH, f'//*[@id="fixtures-list"]/div/div/table/tbody/tr[{i}]/td[1]/div/div[1]').text,
                    driver.find_element(By.XPATH, f'//*[@id="fixtures-list"]/div/div/table/tbody/tr[{i}]/td[2]/div/div/div[2]/span').text,
                    driver.find_element(By.XPATH, f'//*[@id="fixtures-list"]/div/div/table/tbody/tr[{i}]/td[3]/div/div[1]').text
                ]
                rows.append(row_data)
            except NoSuchElementException:
                break

        table_data = f'{hed1}  {hed2}  {hed3}\n\n'
        for row in rows:
            table_data += ' | '.join(row) + '\n'

        return table_data
    except NoSuchElementException as e:
        print(e)
        return "حدث خطأ أثناء جلب النتائج: تأكد من صحة الصفحة."
    except Exception as e:
        print(e)
        return "حدث خطأ غير متوقع أثناء جلب النتائج."

def extract_fixtures_data():
    try:
        hed1, hed2, hed3 = driver.find_element(By.XPATH, '//*[@id="fixtures-list"]/div/div/table/thead/tr/th[1]/span'), driver.find_element(By.XPATH, '//*[@id="fixtures-list"]/div/div/table/thead/tr/th[2]/span'), driver.find_element(By.XPATH, '//*[@id="fixtures-list"]/div/div/table/thead/tr/th[3]/span')
        rows = []
        for i in range(1, 11):
            row = []
            for j in range(1, 4):
                try:
                    cell = driver.find_element(By.XPATH, f'//*[@id="fixtures-list"]/div/div/table/tbody/tr[{i}]/td[{j}]/div/div/a').text
                except:
                    cell = ' vs '
                row.append(cell)
            rows.append(row)
        table_data = f'{hed1.text}  {hed2.text}  {hed3.text}\n\n'
        for row in rows:
            table_data += ' | '.join(row) + '\n'
        return table_data
    except Exception as e:
        return f"حدث خطأ أثناء استخراج بيانات الجولة القادمة: "
def data_analysis():
    try:
        driver.get('https://ar.onlinesoccermanager.com/DataAnalist')
        time.sleep(1)
        driver.find_element(By.XPATH, '//*[@id="spy-team-list"]/div[1]/div/div').click()
       
        '''wait = WebDriverWait(driver, 10)
        
        # Locate the element using its class and the specific inner div structure
        element = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//div[@class='row row-grid-fix-top']//div[contains(@class, 'panel center theme-panna-0 clickable')]")
        ))'''
        
        # Click the element
        #element.click()
        time.sleep(2)
        xpathe = "//div[@class='panel center theme-stepover-0 clickable']"
        if is_element_present(xpathe):
            result = driver.find_element(By.XPATH, xpathe).text
        
        another_team = driver.find_element(By.XPATH, '//*[@id="body-content"]/div[2]/div/div[1]/div/div/div[2]/div[1]').text
        trainer = driver.find_element(By.XPATH, '//*[@id="body-content"]/div[2]/div/div[1]/div/div/div[2]/div[2]').text
        camp = driver.find_element(By.XPATH, '//*[@id="body-content"]/div[2]/div/div[7]/div/div[1]/div/div/span/span').text
        match_plan = driver.find_element(By.XPATH, '//*[@id="body-content"]/div[2]/div/div[3]/div/div[1]/div/div/span/span').text
        pass_cut = driver.find_element(By.XPATH, '//*[@id="body-content"]/div[2]/div/div[6]/div/div[1]/div/div/span/span').text
        controlar  = driver.find_element(By.XPATH, '//*[@id="body-content"]/div[2]/div/div[4]/div/div[1]/div/div/span/span').text
        of_side_catcher = driver.find_element(By.XPATH, '//*[@id="body-content"]/div[2]/div/div[5]/div/div[1]/div/div/span/span').text
        arina = driver.find_element(By.XPATH, '//*[@id="body-content"]/div[2]/div/div[8]/div/div[1]/div/div/span').text
        driver.find_element(By.XPATH, '//*[@id="spy-col-header"]/ul/li[2]/a').click()
        time.sleep(1)
        tashkila = driver.find_element(By.XPATH, '//*[@id="formation-content"]').text
        #taktic
        driver.get('https://ar.onlinesoccermanager.com/Tactics')
        time.sleep(2)
        forwards = driver.find_element(By.XPATH, '//*[@id="carousel-tacticlineatt"]/div[2]/div/div/div[1]/h3').text
        midfielders = driver.find_element(By.XPATH, '//*[@id="carousel-tacticlinemid"]/div[2]/div/div/div[1]/h3').text
        defenders = driver.find_element(By.XPATH, '//*[@id="carousel-tacticlinedef"]/div[2]/div/div/div[1]/h3').text
        pressing = driver.find_element(By.XPATH, '//*[@id="body-content"]/div[3]/div[2]/div[1]/div/div/div/div[2]/div[2]/h5').text
        pressing_dig = driver.find_element(By.XPATH, '//*[@id="body-content"]/div[3]/div[2]/div[1]/div/div/div/div[2]/div[3]/div/div[2]/input').get_attribute('value')
        style = driver.find_element(By.XPATH, '//*[@id="body-content"]/div[3]/div[2]/div[2]/div/div/div/div[2]/div[2]/h5').text
        style_dig = driver.find_element(By.XPATH, '//*[@id="body-content"]/div[3]/div[2]/div[2]/div/div/div/div[2]/div[3]/div/div[2]/input').get_attribute('value')
        tempo = driver.find_element(By.XPATH, '//*[@id="body-content"]/div[3]/div[2]/div[3]/div/div/div/div[2]/div[2]/h5').text
        tempo_dig = driver.find_element(By.XPATH, '//*[@id="body-content"]/div[3]/div[2]/div[3]/div/div/div/div[2]/div[3]/div/div[2]/input').get_attribute('value')

        
        result = f'❏ الفريق الخصم: {another_team}\n❏ المدرب: {trainer}\n❏ التشكيلة: {tashkila}\nء--------------------------------------------------\n❏ أسلوب اللعب: {match_plan}\n❏ قطع الكرة:  {pass_cut}\n❏ مصيدة التسلل:  {of_side_catcher}\n❏ الرقابة: {controlar}\nء--------------------------------------------------\n❏ ارض الملعب:   {arina}\n❏ معسكر التدريب: {camp}\nء--------------------------------------------------\n❏ الهجوم:  {forwards}\n❏ الوسط:  {midfielders}\n❏ الدفاع:  {defenders}\nء--------------------------------------------------\n❏ الضغط على الخصم: {pressing}({pressing_dig})\n❏ الاسلوب: {style}({style_dig})\n❏ ايقاع اللعب:  {tempo}({tempo_dig})'
    except Exception as e :
        
        try:
            err = driver.find_element(By.XPATH, '//*[@id="modal-dialog-sendspy"]/div[4]/div/div/div/div[3]/button')
            if err:
                err.click()
                result = 'تم طلب تحليل البيانات انظر حتى تتم مدة الطلب'
        except:
            pass
        try:
            fe = driver.find_element(By.XPATH, '//*[@id="countdowntimer-panel-container"]/div/div[2]/div[2]').text
            if fe:
                result = f'الوقت المتبقي: {fe}'
        except:
            pass
        try:
            opn = driver.find_element(By.XPATH, '//*[@id="countdowntimer-panel-container"]/div/div/div[3]/button')
            if opn:
                opn.click()
                result = f'❏ الفريق الخصم: {another_team}\n❏ المدرب: {trainer}\n❏ التشكيلة: {tashkila}\nء--------------------------------------------------\n❏ أسلوب اللعب: {match_plan}\n❏ قطع الكرة:  {pass_cut}\n❏ مصيدة التسلل:  {of_side_catcher}\n❏ الرقابة: {controlar}\nء--------------------------------------------------\n❏ ارض الملعب:   {arina}\n❏ معسكر التدريب: {camp}\nء--------------------------------------------------\n❏ الهجوم:  {forwards}\n❏ الوسط:  {midfielders}\n❏ الدفاع:  {defenders}\nء--------------------------------------------------\n❏ الضغط على الخصم: () {pressing}({pressing_dig})\n❏ الاسلوب: () {style}({style_dig})\n❏ ايقاع اللعب:  {tempo}({tempo_dig})'
    
        except:
            pass
        result = f" حدث خطأ أثناء استخراج بيانات التحليل الرجاء التأكد من حالة محلل البيانات !"
    return result
# تحقق من وجود العنصر
def is_element_present(xpath):
    elements = driver.find_elements(By.XPATH, xpath)
    return len(elements) > 0
  # Replace with your user database or tracking method
@bot.message_handler(commands=['help'])
def send_help(message):
    help_text = (
        '''لاستخدام هذا الروبوت، اتبع الخطوات التالية:

1. قم بتسجيل الدخول إلى حسابك باستخدام اسمك باللعبة وكلمة المرور.
2. بعد تسجيل الدخول، اختر فتحة فريقك لعرض نتائج التجسس.
3. يرجى التأكد من أنك قمت بإرسال محلل البيانات مسبقًا وقمت بفتح النتائج المرتجعة لرؤية معلومات إضافية.

🚨 هذا البوت يتبع بوت المدرب الأفضل ويشرف عليه ساكو @sako7osm

🛍 لشحن الكوينز و ملايين المدرب الأفضل ادخل المتجر واختار باقتك بعنايه : t.me/Dani5zzbot
للتعليق على مشاكل البوت - مطور البوت: @hemonybot
'''
        
        # Add more commands as needed
    )
    bot.send_message(message.chat.id, help_text)
# Function to log out from OSM account
def osm_logout():
    try:
        # Open the OSM website (replace with the actual URL)
        

        # Wait until the profile menu/icon is visible
        wait = WebDriverWait(driver, 10)
        
        # Assuming there's a profile icon/menu to click on for logging out
        profile_icon = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@class='profile-menu-icon']")))
        profile_icon.click()

        # Wait until the logout button/link is visible and clickable
        logout_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Log Out')]")))
        logout_button.click()

        print("Logged out successfully.")

    except Exception as e:
        print("Error logging out:", e)
    finally:
        # Close the browser after logging out
        driver.quit()

users = {}

# لتتبع آخر تفاعل لكل مستخدم
last_active = {}

# دالة التفاعل
def update_activity(user_id):
    last_active[user_id] = datetime.now()

# معالجة أمر /start
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    bot.send_message(message.chat.id, f"مرحبًا، {message.from_user.first_name}!")
    
    # إضافة المستخدم إلى القاعدة
    if user_id not in users:
        users[user_id] = message.from_user.username or message.from_user.first_name
    update_activity(user_id)

# معالجة أمر /admin
@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.from_user.id == ADMIN_ID:
        markup = types.ReplyKeyboardMarkup(row_width=2)
        btn1 = types.KeyboardButton('نشر رسالة')
        btn2 = types.KeyboardButton('حذف مستخدم')
        btn3 = types.KeyboardButton('إحصائيات المستخدمين')
        btn4 = types.KeyboardButton('تمييز المستخدمين')
        btn5 = types.KeyboardButton('اضافة كمدفوع')
        btn6 = types.KeyboardButton('حذف من المدفوع')
        markup.add(btn1, btn2, btn3, btn4, btn5, btn6)
        bot.send_message(message.chat.id, "لوحة التحكم الخاصة بالإدارة:", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "أنت غير مصرح لك بالدخول إلى هذه اللوحة.")

# التعامل مع النصوص الصادرة من لوحة الإدارة
# تأكد من تعريف ADMIN_ID و PRINUM_USERS في مكان ما في الكود الخاص بك.
# ADMIN_ID هو معرف المدير، و PRINUM_USERS هي قائمة تحتوي على معرفات المستخدمين المدفوعين.

@bot.message_handler(func=lambda message: message.text in ['نشر رسالة', 'حذف مستخدم', 'إحصائيات المستخدمين', 'تمييز المستخدمين', 'اضافة كمدفوع', 'حذف من المدفوع'])
def admin_actions(message):
    if message.from_user.id == ADMIN_ID:
        if message.text == 'نشر رسالة':
            bot.send_message(message.chat.id, "الرجاء إرسال الرسالة التي ترغب في نشرها.")
            bot.register_next_step_handler(message, send_broadcast)
        
        elif message.text == 'حذف مستخدم':
            bot.send_message(message.chat.id, "الرجاء إرسال معرف المستخدم الذي ترغب في حذفه.")
            bot.register_next_step_handler(message, delete_user)
        
        elif message.text == 'إحصائيات المستخدمين':
            user_statistics(message)
        
        elif message.text == 'تمييز المستخدمين':
            categorize_users(message)
        
        elif message.text == 'اضافة كمدفوع':
            bot.send_message(message.chat.id, "الرجاء إرسال ايدي المستخدم الذي ترغب في اضافته كمدفوع.")
            bot.register_next_step_handler(message, add_paid_user)
        
        elif message.text == 'حذف من المدفوع':
            bot.send_message(message.chat.id, "الرجاء إرسال ايدي المستخدم الذي ترغب في حذفه من قائمة المدفوع.")
            bot.register_next_step_handler(message, remove_paid_user)
    else:
        bot.send_message(message.chat.id, "أنت غير مصرح لك بالقيام بهذا الإجراء.")

# إضافة مستخدم مدفوع
def add_paid_user(message):
    user_id = int(message.text)
    if user_id not in PRINUM_USERS:
        PRINUM_USERS.append(user_id)
        bot.send_message(message.chat.id, f"تمت إضافة المستخدم {user_id} كمدفوع.")
    else:
        bot.send_message(message.chat.id, f"المستخدم {user_id} موجود بالفعل في قائمة المدفوع.")

# حذف مستخدم مدفوع
def remove_paid_user(message):
    user_id = int(message.text)
    if user_id in PRINUM_USERS:
        PRINUM_USERS.remove(user_id)
        bot.send_message(message.chat.id, f"تم حذف المستخدم {user_id} من قائمة المدفوع.")
    else:
        bot.send_message(message.chat.id, f"المستخدم {user_id} غير موجود في قائمة المدفوع.")
# دالة نشر الرسائل
def send_broadcast(message):
    broadcast_msg = message.text
    for user_id in users:
        bot.send_message(user_id, f"رسالة من الإدارة: {broadcast_msg}")
    bot.send_message(ADMIN_ID, "تم إرسال الرسالة إلى جميع المستخدمين.")

# دالة حذف المستخدم
def delete_user(message):
    try:
        user_id_to_delete = int(message.text)
        if user_id_to_delete in users:
            del users[user_id_to_delete]
            if user_id_to_delete in last_active:
                del last_active[user_id_to_delete]
            bot.send_message(ADMIN_ID, f"تم حذف المستخدم {user_id_to_delete}.")
        else:
            bot.send_message(ADMIN_ID, "المستخدم غير موجود.")
    except ValueError:
        bot.send_message(ADMIN_ID, "معرف المستخدم غير صحيح.")

# دالة عرض إحصائيات المستخدمين
def user_statistics(message):
    total_users = len(users)
    active_users = sum(1 for t in last_active.values() if datetime.now() - t < timedelta(days=7))
    inactive_users = total_users - active_users
    bot.send_message(ADMIN_ID, f"إحصائيات المستخدمين:\nإجمالي المستخدمين: {total_users}\nالمستخدمين المتفاعلين: {active_users}\nالمستخدمين الخاملين: {inactive_users}")

# دالة تمييز المستخدمين
def categorize_users(message):
    active_users = []
    inactive_users = []
    for user_id, last_time in last_active.items():
        if datetime.now() - last_time < timedelta(days=7):
            active_users.append(f"{user_id}: {users[user_id]}")
        else:
            inactive_users.append(f"{user_id}: {users[user_id]}")
    
    active_list = "\n".join(active_users)
    inactive_list = "\n".join(inactive_users)
    
    bot.send_message(ADMIN_ID, f"المستخدمون المتفاعلون:\n{active_list}")
    bot.send_message(ADMIN_ID, f"المستخدمون الخاملون:\n{inactive_list}")

#time.sleep(250)
# تشغيل البوت
bot.polling()

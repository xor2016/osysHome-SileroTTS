import datetime
import re
units = (
    u'ноль',

    (u'один', u'одна'),
    (u'два', u'две'),

    u'три', u'четыре', u'пять',
    u'шесть', u'семь', u'восемь', u'девять'
)

teens = (
    u'десять', u'одиннадцать',
    u'двенадцать', u'тринадцать',
    u'четырнадцать', u'пятнадцать',
    u'шестнадцать', u'семнадцать',
    u'восемнадцать', u'девятнадцать'
)

tens = (
    teens,
    u'двадцать', u'тридцать',
    u'сорок', u'пятьдесят',
    u'шестьдесят', u'семьдесят',
    u'восемьдесят', u'девяносто'
)

hundreds = (
    u'сто', u'двести',
    u'триста', u'четыреста',
    u'пятьсот', u'шестьсот',
    u'семьсот', u'восемьсот',
    u'девятьсот'
)

orders = (
    ((u'тысяча', u'тысячи', u'тысяч'), 'f'),
    ((u'миллион', u'миллиона', u'миллионов'), 'm'),
    ((u'миллиард', u'миллиарда', u'миллиардов'), 'm'),
)

minus = u'минус'


def thousand(rest, sex):
    prev = 0
    plural = 2
    name = []
    use_teens = 10 <= rest % 100 <= 19
    if not use_teens:
        data = ((units, 10), (tens, 100), (hundreds, 1000))
    else:
        data = ((teens, 10), (hundreds, 1000))
    for names, x in data:
        cur = int(((rest - prev) % x) * 10 / x)
        prev = rest % x
        if x == 10 and use_teens:
            plural = 2
            name.append(teens[cur])
        elif cur == 0:
            continue
        elif x == 10:
            name_ = names[cur]
            if isinstance(name_, tuple):
                name_ = name_[0 if sex == 'm' else 1]
            name.append(name_)
            if 2 <= cur <= 4:
                plural = 1
            elif cur == 1:
                plural = 0
            else:
                plural = 2
        else:
            name.append(names[cur - 1])
    return plural, name


def num2text(num, main_units=((u'', u'', u''), 'm'), mns = 0):
    _orders = (main_units,) + orders
    if num == 0:
        if mns == 1:
            return minus +' ' + (' '.join((units[0], _orders[0][0][2])).strip())
        return ' '.join((units[0], _orders[0][0][2])).strip()

    rest = abs(num)
    ord = 0
    name = []
    while rest > 0:
        plural, nme = thousand(rest % 1000, _orders[ord][1])
        if nme or ord == 0:
            name.append(_orders[ord][0][plural])
        name += nme
        rest = int(rest / 1000)
        ord += 1
   
    if num < 0:
        name.append(minus)
    name.reverse()
    return ' '.join(name).strip()

   
def d2t(value, places=1,
                 int_units=(('', '', ''), 'm'),
                 exp_units=(('', '', ''), 'm')):
    mns=0
    if places>2:
        places = 2
    if value<0:
        mns = 1 #параметр для дробей вида -0,хх
    value = abs(value)
    value = round(value, places)
    if int_units[0][0] == '':
        int_units = ((u'целая', u'целых', u'целых'), 'f')
        if places == 2:
            exp_units = ((u'сотая', u'сотых', u'сотых'), 'f')
        else:
            exp_units = ((u'десятая', u'десятых', u'десятых'), 'f')
    i, d = divmod(value, 1)
    d = round(d, places)
    int_v=int(i)
    exp_v=int(d*10**places)
    
    if mns == 1:
        int_v = -1*int_v
    if exp_v == 0:
        return u'{} '.format(num2text(int_v, (('', '', ''), 'm'), mns))
    else:    
        return u'{} {}'.format(
        num2text(int_v, int_units, mns),
        num2text(exp_v, exp_units),0)

def f_ctime():
    now = datetime.datetime.now()
    text = "Сейчас "
    male_units = ((u'час', u'часа', u'часов'), 'm')
    text += num2text(int(now.hour), male_units) + ' '
    male_units = ((u'минута', u'минуты', u'минут'), 'f')
    text += num2text(int(now.minute), male_units) + '.'
    return text

def convert_time(match_obj):
    if match_obj.group() is not None:
        text = str(match_obj.group())
        parts = text.split(":")
        hr = int(parts[0])
        mn = int(parts[1])
        hr_units = ((u'час', u'часа', u'часов'), 'm')
        text = num2text(hr, hr_units) + ' '
        mn_units = ((u'минута', u'минуты', u'минут'), 'f')
        text += num2text(mn, mn_units) + ' '
        return text

def convert_one_num_float(match_obj):
    if match_obj.group() is not None:
        text = str(match_obj.group())
        return d2t(float(match_obj.group()))

def convert_grad(match_obj):
    if match_obj.group() is not None:    
        text = str(match_obj.group())
        text = text.replace("°","")
        return num2text(int(text),((u'градус', u'градуса', u'градусов'), 'm'))

def convert_proc(match_obj):
    if match_obj.group() is not None:    
        text = str(match_obj.group())
        text = text.replace("%"," ")
        return num2text(int(text),((u'процент', u'процента', u'процентов'), 'm'))

def convert_ms(match_obj):
    if match_obj.group() is not None:    
        text = str(match_obj.group())
        text = text.replace(" м/с"," ")
        return num2text(int(text),((u'метр в секунду', u'метра в секунду', u'метров в секунду'), 'm'))
    
def convert_pt(match_obj):
    if match_obj.group() is not None:    
        text = str(match_obj.group())
        text = text.replace(" мм рт.ст."," ")
        return num2text(int(text),((u'миллиметр ', u'миллиметра ', u'миллиметров'), 'm'))
  
def convert_diapazon(match_obj):
    if match_obj.group() is not None:
        text = str(match_obj.group())
        text = text.replace("-"," тире ")        
        return all_num_to_text(text)
    
def convert_short_date(match_obj): #21 февраля to-do
    if match_obj.group() is not None:
        text = str(match_obj.group())
        parts = text.split()
        day = int(parts[0])
        if day>=1 and day<=31:
            days = ['нулевое','первое','второе','третье','четвертое','пятое','шестое','седьмое','восьмое','девятое','десятое','одиннадцатое','двенадцатое','тринадцатое','четырнадцатое','пятнадцатое','шестнадцатое','семнадцатое','восемнадцатое','девятнадцатое','двадцатое','двадцать первое','двадцать второе','двадцать третье','двадцать четвертое','двадцать пятое','двадцать шестое','двадцать седьмое','двадцать восьмое','двадцать девятое','тридцатое','тридцать первое']
            myday = days[day]
            text = text.replace(parts[0],days[day])        
        return text
    
def all_num_to_text(text:str) -> str:
    text = re.sub(r'[\d]*[.][\d]+-[\d]*[.][\d]+', convert_diapazon, text)
    text = re.sub(r'-[\d]+°',convert_grad, text)    
    text = re.sub(r'[\d]+°',convert_grad, text)
    text = re.sub(r'-[\d]+%',convert_proc, text)     
    text = re.sub(r'[\d]+%',convert_proc, text)
    text = re.sub(r'[\d]+ м\/с',convert_ms, text)
    text = re.sub(r'[\d]+ мм рт.ст.',convert_pt, text)
    text = re.sub(r'[\d]+:[\d]+',convert_time, text)
    text = re.sub(r'[\d]+ (января|февраля|мая|июня|июля|августа|сентября|октября|ноября|декабря)',convert_short_date,text)
    text = re.sub(r'-[\d]*[.][\d]+', convert_one_num_float, text)
    text = re.sub(r'[\d]*[.][\d]+', convert_one_num_float, text)
    text = re.sub(r'[\d]+-[\d]+', convert_diapazon, text)
    text = re.sub(r'-[\d]+', convert_one_num_float, text)
    text = re.sub(r'[\d]+', convert_one_num_float, text)
    return text
if __name__ == "__main__":
    print(f_ctime())
    print(d2t(-0.048,2))
    print(all_num_to_text(" Домодедово, 02 июля: Облачно, без осадков. Температура ночью 015°, днём 30°. Ветер юго-западный, 1 м/с. Атмосферное давление ночью 747 мм, днём 747 мм. Вероятность осадков 15%"))
 




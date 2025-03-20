from flask import Flask, render_template, request, send_file, redirect, url_for
import os
import uuid
from datetime import datetime, timedelta
import ics
from ics import Calendar, Event
from lunardate import LunarDate
import json
import pickle

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', os.urandom(24))
app.config['UPLOAD_FOLDER'] = 'temp'

# 確保臨時目錄存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# 存儲朋友生日數據的字典
friends_data = {}

# 嘗試從文件加載數據
data_file = 'friends_data.pkl'
try:
    if os.path.exists(data_file):
        with open(data_file, 'rb') as f:
            friends_data = pickle.load(f)
except Exception as e:
    print(f"Error loading data: {e}")

@app.route('/', methods=['GET'])
def index():
    current_year = datetime.now().year
    return render_template('index.html', friends=friends_data, current_year=current_year)

@app.route('/add_friend', methods=['POST'])
def add_friend():
    name = request.form.get('name')
    calendar_type = request.form.get('calendar_type')
    
    # 生成唯一ID
    friend_id = str(uuid.uuid4())
    
    # 根據日曆類型存儲朋友信息
    if calendar_type == 'lunar':
        lunar_month = int(request.form.get('lunar_month'))
        lunar_day = int(request.form.get('lunar_day'))
        
        friends_data[friend_id] = {
            'name': name,
            'calendar_type': 'lunar',
            'lunar_month': lunar_month,
            'lunar_day': lunar_day
        }
    else:  # solar
        solar_month = int(request.form.get('solar_month'))
        solar_day = int(request.form.get('solar_day'))
        
        friends_data[friend_id] = {
            'name': name,
            'calendar_type': 'solar',
            'solar_month': solar_month,
            'solar_day': solar_day
        }
    
    # 保存數據到文件
    try:
        with open(data_file, 'wb') as f:
            pickle.dump(friends_data, f)
    except Exception as e:
        print(f"Error saving data: {e}")
    
    return redirect(url_for('index'))

@app.route('/remove_friend/<friend_id>', methods=['POST'])
def remove_friend(friend_id):
    if friend_id in friends_data:
        del friends_data[friend_id]
        # 保存數據到文件
        try:
            with open(data_file, 'wb') as f:
                pickle.dump(friends_data, f)
        except Exception as e:
            print(f"Error saving data: {e}")
    return redirect(url_for('index'))

@app.route('/generate_ics', methods=['POST'])
def generate_ics():
    # 創建日曆
    cal = Calendar()
    
    # 獲取用戶選擇的年份範圍
    start_year = int(request.form.get('start_year', datetime.now().year))
    end_year = int(request.form.get('end_year', datetime.now().year + 5))
    
    # 根據選擇的年份範圍創建生日事件
    for year in range(start_year, end_year + 1):
        for friend_id, friend in friends_data.items():
            try:
                event = Event()
                event.name = friend['name']
                
                # 根據日曆類型處理日期
                if friend.get('calendar_type') == 'lunar':
                    # 將農曆日期轉換為西曆日期
                    lunar_date = LunarDate(year, friend['lunar_month'], friend['lunar_day'])
                    solar_date = lunar_date.toSolarDate()
                    
                    event.begin = datetime(solar_date.year, solar_date.month, solar_date.day)
                    event.description = f"今天是{friend['name']}的農曆生日（農曆{friend['lunar_month']}月{friend['lunar_day']}日）"
                else:  # solar
                    # 直接使用西曆日期
                    event_date = datetime(year, friend['solar_month'], friend['solar_day'])
                    event.begin = event_date
                    event.description = f"今天是{friend['name']}的西曆生日（西曆{friend['solar_month']}月{friend['solar_day']}日）"
                
                event.make_all_day()
                # 添加到日曆
                cal.events.add(event)
            except Exception as e:
                print(f"Error processing {friend['name']}'s birthday: {e}")
    
    # 生成ICS文件
    ics_filename = f"birthdays_{uuid.uuid4()}.ics"
    ics_path = os.path.join(app.config['UPLOAD_FOLDER'], ics_filename)
    
    with open(ics_path, 'w') as f:
        f.write(str(cal))
    
    # 自定義下載檔案名稱，包含年份範圍
    download_name = f"friends_birthdays_{start_year}_{end_year}.ics"
    
    return send_file(ics_path, as_attachment=True, download_name=download_name)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
import pandas as pd
import numpy as np  
import matplotlib.pyplot as plt
import xml.etree.ElementTree as ET


# 设置中文字体为微软雅黑 中文需要添加
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']
# 用来正常显示负号
plt.rcParams['axes.unicode_minus'] = False


def convert_seconds_to_minutes(seconds):
    # 计算分钟数
    minutes = seconds // 60
    # 计算剩余秒数
    remaining_seconds = seconds % 60
    # 返回分钟和剩余秒数的元组
    return (minutes, remaining_seconds)

# 计算配速
def convert_speed_to_pace(speed_mps):  
    # 计算配速（每公里时间）  
    pace_per_km_seconds = 1/  speed_mps /60 * 1000    
    # 返回配速（分钟/公里）  
    return pace_per_km_seconds
  
# 示例  
speed_in_mps = 4.5  # 假设速度是4.5米/秒  
pace_in_min_km = convert_speed_to_pace(speed_in_mps)  
print(f"速度是 {speed_in_mps} 米/秒 的配速是 {pace_in_min_km}。")



# 定义命名空间
ns = {'ns': 'http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2',
      'ns2': 'http://www.garmin.com/xmlschemas/ActivityExtension/v2',
      'ns3': 'http://www.garmin.com/xmlschemas/ActivityExtension/v2'}

# 读取TCX文件
tree = ET.parse('Zepp20240218175205.tcx')
root = tree.getroot()

# 提取数据1
trackpoints = root.findall('.//ns:Trackpoint', ns)
data = []
for tp in trackpoints:
    try:
        lat = float(tp.find('ns:Position/ns:LatitudeDegrees', ns).text)
    except Exception as e:
        lat = None

    try:
        lon = float(tp.find('ns:Position/ns:LongitudeDegrees', ns).text)
    except Exception as e:
        lon = None

    try:
        altitude = float(tp.find('ns:AltitudeMeters', ns).text)
    except Exception as e:
        altitude = None    

    try:
        heart_rate = float(tp.find('ns:HeartRateBpm/ns:Value', ns).text)
    except Exception as e:
        heart_rate = None

    try:
        cadence = float(tp.find('ns:Cadence', ns).text)
    except Exception as e:
        cadence = None

    try:
        speed = float(tp.find('ns:Extensions/ns3:TPX/ns3:Speed', ns).text)
        pace = convert_speed_to_pace(speed)
    except Exception as e:
        pace = None
        speed = None

    try:
        Time = pd.to_datetime((tp.find('ns:Time', ns).text))
        Time = pd.to_datetime(Time,format="ISO8601", utc=True)
        Time = pd.to_datetime(Time.tz_convert("Asia/Shanghai"))
    except Exception as e:
        Time = None

    data.append([Time,lat, lon, altitude, heart_rate, cadence, speed, pace])

# 创建DataFrame
df = pd.DataFrame(data, columns=['Time','Latitude', 'Longitude', 'Altitude', 'HeartRate', 'Cadence','speed', 'pace'])

df = df[df.pace <= 20]  #过滤掉休息的配速  配速低于20过滤
#

total_time_element = root.find(".//ns:Id",namespaces=ns)

TotalTimeSeconds = (root.find('.//ns:TotalTimeSeconds',namespaces=ns)).text
DistanceMeters = (root.find('.//ns:DistanceMeters',namespaces=ns)).text
Calories = (root.find('.//ns:Calories',namespaces=ns)).text
AverageHeartRateBpm = (root.find('.//ns:AverageHeartRateBpm/ns:Value',namespaces=ns)).text

#打印4大数值
print(TotalTimeSeconds,DistanceMeters,Calories,AverageHeartRateBpm)

#打印df
print(df)


###########
plt.subplot(2, 2, 1)  # 创建1行2列的图形，并选择第1个图形
# 创建第一个图形
plt.plot(df.Time,df.Altitude,color='r')    
plt.plot(df.Time,df.Cadence,color='b')
plt.grid(True)
plt.xticks(rotation=90) 
plt.title('高度(米)')
#plt.colorbar()
# 创建第二个图形
plt.subplot(2, 2, 2)  # 创建1行2列的图形，并选择第2个图形
plt.scatter(x=df.Longitude,y=df.Latitude,c=df.pace,cmap='RdYlBu',s=2) #速度
plt.colorbar()
plt.title('配速(分钟/公里)')   
# 创建第三个图形
plt.subplot(2, 2, 3)
plt.plot(df.Time,df.pace,color='r')   
plt.xticks(rotation=90) 
plt.grid(True)
plt.title('配速(分钟/公里)') 
# 创建第四个图形
plt.subplot(2, 2, 4)
plt.scatter(x=df.Longitude,y=df.Latitude,c=df.HeartRate,s=2) #高度
plt.title('心率')   
plt.colorbar()


minutes, remaining_seconds = convert_seconds_to_minutes(int(TotalTimeSeconds))
plt.suptitle( f"时间:{minutes}:{remaining_seconds}      距离:{DistanceMeters}m      热量:{Calories}     平均心率:{AverageHeartRateBpm}", fontsize=16)
plt.show()











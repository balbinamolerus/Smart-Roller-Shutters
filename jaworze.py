# autostart:
#  sudo apt-get install nodejs npm
#  sudo npm install pm2@latest -g
#  pm2 startup
#  pm2 start script.py
#  pm2 save
#  reboot

import paho.mqtt.client as mqtt
from astral import Astral
import time
from datetime import datetime, date

all_down = False
all_up = False
city_name = 'Warsaw'
a = Astral()
a.solar_depression = 'civil'
city = a[city_name]


def on_message(client, userdata, message):
    global all_down, all_up

    if message.topic == "shellies/main/input/0" and str(message.payload.decode("utf-8")) == "1":
        all_down = True

    if message.topic == "shellies/main/input/1" and str(message.payload.decode("utf-8")) == "1":
        all_up = True


def command_all(message):
    client.publish("shellies/salon1/roller/0/command", message, qos=1, retain=True)
    client.publish("shellies/salon2/roller/0/command", message, qos=1, retain=True)
    client.publish("shellies/salon3/roller/0/command", message, qos=1, retain=True)
    client.publish("shellies/kuchnia/roller/0/command", message, qos=1, retain=True)
    client.publish("shellies/spizarnia/roller/0/command", message, qos=1, retain=True)
    client.publish("shellies/garaz/roller/0/command", message, qos=1, retain=True)
    client.publish("shellies/lazienka1/roller/0/command", message, qos=1, retain=True)
    client.publish("shellies/wiatrolap/roller/0/command", message, qos=1, retain=True)
    client.publish("shellies/gabinet/roller/0/command", message, qos=1, retain=True)
    client.publish("shellies/lazienka2/roller/0/command", message, qos=1, retain=True)
    client.publish("shellies/sypialnia/roller/0/command", message, qos=1, retain=True)
    client.publish("shellies/kuba/roller/0/command", message, qos=1, retain=True)
    client.publish("shellies/balbi/roller/0/command", message, qos=1, retain=True)


broker_address = "192.168.1.xxx"
client = mqtt.Client()
client.username_pw_set("xxxxx", "xxxxxxxx")
client.on_message = on_message
client.connect(broker_address, 1883)

client.subscribe(
    [("shellies/main/input/0", 1), ("shellies/main/input/1", 1)])

command_all("open")
client.loop_start()

n = 0
has_closed = False
has_opened = False
sunset_minute = 40
sunset_hour = 0
sunrise_minute = -40
sunrise_hour = 0
date_now = date.today()
sun = city.sun(date=date(datetime.now().year, datetime.now().month, datetime.now().day), local=True)

while True:
    if n > 500:
        n = 0
        try:
            sun = city.sun(date=date(datetime.now().year, datetime.now().month, datetime.now().day), local=True)
        except:
            pass
        sunset_minute = 40
        sunrise_minute = -40
        if date.today() != date_now:
            date_now = date.today()
            has_closed = False
            has_opened = False

        now_minute = datetime.now().minute
        now_hour = datetime.now().hour

        sunrise_minute += sun['sunrise'].minute
        if sunrise_minute < 0:
            sunrise_minute += 60
            sunrise_hour = sun['sunrise'].hour - 1
        else:
            sunrise_hour = sun['sunrise'].hour
        if sunrise_hour >= 6:
            sunrise_hour = 6
            sunrise_minute = 0
        sunset_minute += sun['sunset'].minute
        if sunset_minute > 59:
            sunset_minute -= 60
            sunset_hour = sun['sunset'].hour + 1
        else:
            sunset_hour = sun['sunset'].hour

        if (now_hour > sunrise_hour or (now_hour == sunrise_hour and now_minute > sunrise_minute)) and not has_opened:
            command_all("open")
            print("opening")
            has_opened = True

        if (now_hour > sunset_hour or (now_hour == sunset_hour and now_minute > sunset_minute)) and not has_closed:
            command_all("close")
            print("closing")
            has_closed = True

    if all_down:
        command_all("close")
        all_down = False

    if all_up:
        command_all("open")
        all_up = False
    n += 1
    time.sleep(0.1)

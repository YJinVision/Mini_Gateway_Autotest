import uuid
import threading
import paho.mqtt.publish
import paho.mqtt.subscribe


def on_message(client, userdata, message):
    global msg_que
    payload = message.payload.decode('utf-8')
    topic = message.topic
    # 重組topic及payload成json格式再放入queue
    msg = '{"Topic":"%s", "Payload":{%s}' %(topic, payload[1:])
    msg_que.append(msg)    
    
    if "AUTOTEST_STOP_MQTT_SUBSCRIBE" in payload:
        client.disconnect()

    if __name__ == "__main__":
        print(f"topic:{message.topic},  payload:{msg}")

def sub_loop(broker, topic, daemon_flag=False):
    global msg_que
    msg_que = []
    mac = uuid.UUID(int = uuid.getnode()).hex[-4:].upper()
    def th():
        global sub_flag
        sub_flag = True
        try:
            paho.mqtt.subscribe.callback(callback=on_message, 
                                         topics=topic, 
                                         hostname=broker, 
                                         client_id=f"mqtt_lite_{mac}")
            print(f"MQTT disconnect.")
        except Exception as err:
            sub_flag = False
            print(f"Subscribe failed:\n{err}")
        
    threading.Thread(target=th, daemon=daemon_flag).start()

    
def pub_msg(broker: str, topic: str, msg, client_id="mqtt_lite"):
    
    try:
        paho.mqtt.publish.single(topic=topic, 
                                 payload=str(msg), 
                                 hostname=broker, 
                                 client_id=client_id)
        # print("Message sended.")
        return True
    except:
        # print("Send message failed.")
        return False

if __name__ == "__main__":
    sub_loop("broker.emqx.io", "Vision_V2B")

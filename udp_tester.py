import socket
import threading
import sys

def start_listen(port):
    """
    開始循環監聽UDP訊息(0.0.0.0)，並將訊息放入udp_que: list[str]。
    當收到訊息內容包含"STOP_LISTENING_UDP"時，結束監聽循環。
    Args:
        port: 監聽port號

    """
    global udp_que
    udp_que = []
    def th():
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.bind(("0.0.0.0", port))
        except Exception as err:
            sys.stdout.write(f"[ERROR] 監聽UDP時發生錯誤: {err}")

        while True:
            data, addr = sock.recvfrom(1024) # Buffer size 1024 bytes
            udp_que.append(data.decode())
            if __name__ == "__main__":
                print(data.decode())
            if "STOP_LISTENING_UDP" in data.decode():
                print(f"[INFO] 結束監聽UDP")
                break

    threading.Thread(target=th, 
                     daemon=True
                     ).start()
    
def send_message(ip: str, port, message):
    """
    發送UDP訊息。

    Args:
        ip: str 
        port: str 發送port號
        message: str 要發送的訊息
    
    Return:
        成功:True, 失敗:False : bool
    """
    subnet = ip.rsplit(".", 1)[0] + ".255"
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
        sock.sendto(bytes(message, "utf-8"), (subnet, port))
        return True
    except Exception as err:
        print(f"[ERROR] 發送UDP訊息時發生錯誤: {err}")
        return False

if __name__ == "__main__":
    start_listen(50109)

    input()
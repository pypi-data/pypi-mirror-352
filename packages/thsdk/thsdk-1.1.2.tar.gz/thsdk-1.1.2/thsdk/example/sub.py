import threading
import time
from ctypes import c_char_p, CFUNCTYPE
from thsdk import THS

# 用于控制线程退出的全局事件
exit_event = threading.Event()

# 定义回调函数
@CFUNCTYPE(None, c_char_p)
def callback(data: c_char_p):
    try:
        decoded_data = data.decode('utf-8')
        print(f"收到订阅数据: {decoded_data}")
    except UnicodeDecodeError:
        print("回调数据解码失败")

def run_subscription():
    ths = THS()

    # 连接服务器
    response = ths.connect()
    if response.errInfo != "":
        print(f"连接失败: {response.errInfo}")
        return

    # 订阅实时数据
    response = ths.subscribe(req="test", service_type="push", callback=callback)
    if response.errInfo != "":
        print(f"订阅失败: {response.errInfo}")
        return
    sub_id = response.payload.subscribe_id
    print(f"订阅成功，订阅ID: {sub_id}, 结果: {response.errInfo}")

    

    # 等待退出信号
    try:
        while not exit_event.is_set():
            time.sleep(1)  # 降低 CPU 使用率
    except KeyboardInterrupt:
        print("订阅线程收到中断信号")
    finally:
        # 清理资源
        ths.unsubscribe(sub_id)
        ths.disconnect()
        print("✅ 订阅线程已清理资源并退出")

# 启动订阅线程
if __name__ == "__main__":
    subscription_thread = threading.Thread(target=run_subscription)
    subscription_thread.start()

    # 主线程可以执行其他任务
    try:
        while True:
            print("主线程运行中...")
            time.sleep(5)
    except KeyboardInterrupt:
        print("主线程收到中断信号，通知订阅线程退出")
        exit_event.set()  # 通知订阅线程退出
        subscription_thread.join()  # 等待订阅线程结束
        print("✅ 主线程退出")
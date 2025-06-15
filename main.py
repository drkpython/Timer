import time
import threading
import pyttsx3
from datetime import datetime


class VoiceTimer:
    def __init__(self):
        # 计时相关变量
        self.start_time = None
        self.timer_running = False
        self.voice_thread = None
        self.stop_voice = False

    def speak(self, text):
        """语音播报（异步方式）"""

        def _speak():
            try:
                # 创建新的引擎实例避免冲突
                engine = pyttsx3.init()
                engine.setProperty('rate', 150)
                engine.setProperty('volume', 0.8)
                engine.say(text)
                engine.runAndWait()
                engine.stop()
            except Exception as e:
                print(f"语音播报失败: {e}")

        # 在单独线程中执行语音播报
        threading.Thread(target=_speak, daemon=True).start()

    def voice_announce(self):
        """每10秒语音播报一次"""
        counter = 0
        while self.timer_running and not self.stop_voice:
            # 每秒检查一次状态，避免长时间sleep被阻塞
            time.sleep(1)
            counter += 1

            if counter >= 10 and self.timer_running and not self.stop_voice:
                elapsed = int(time.time() - self.start_time)
                minutes = elapsed // 60
                seconds = elapsed % 60

                if minutes > 0:
                    announcement = f" {minutes} 分 {seconds} 秒"
                else:
                    announcement = f" {seconds} 秒"

                print(f"[{datetime.now().strftime('%H:%M:%S')}] {announcement}")
                self.speak(announcement)
                counter = 0  # 重置计数器

    def start_timer(self):
        """开始计时"""
        # 停止之前的语音线程
        if self.voice_thread and self.voice_thread.is_alive():
            self.stop_voice = True
            self.voice_thread.join(timeout=1)

        # 重置并开始新的计时
        self.start_time = time.time()
        self.timer_running = True
        self.stop_voice = False

        print(f"[{datetime.now().strftime('%H:%M:%S')}] 计时开始！")
        self.speak("计时开始")

        # 启动语音播报线程
        self.voice_thread = threading.Thread(target=self.voice_announce, daemon=True)
        self.voice_thread.start()

    def stop_timer(self):
        """停止计时"""
        if self.timer_running:
            self.timer_running = False
            self.stop_voice = True

            elapsed = int(time.time() - self.start_time)
            minutes = elapsed // 60
            seconds = elapsed % 60

            if minutes > 0:
                final_time = f"总计时间: {minutes} 分 {seconds} 秒"
            else:
                final_time = f"总计时间: {seconds} 秒"

            print(f"[{datetime.now().strftime('%H:%M:%S')}] 计时结束！{final_time}")
            self.speak(f"计时结束，{final_time}")

    def run(self):
        """主运行循环"""
        print("=== 语音计时器 ===")
        print("按回车开始/重新开始计时")
        print("输入 'q' 并按回车退出程序")
        print("每10秒会自动语音播报当前时间")
        print("-" * 30)

        try:
            while True:
                user_input = input().strip().lower()

                if user_input == 'q':
                    if self.timer_running:
                        self.stop_timer()
                    print("程序退出")
                    break
                else:
                    # 按回车开始/重新开始计时
                    self.start_timer()

        except KeyboardInterrupt:
            print("\n程序被中断")
            if self.timer_running:
                self.stop_timer()


def main():
    # 检查是否安装了pyttsx3
    try:
        import pyttsx3
    except ImportError:
        print("错误: 需要安装 pyttsx3 库")
        print("请运行: pip install pyttsx3")
        return

    timer = VoiceTimer()
    timer.run()


if __name__ == "__main__":
    main()
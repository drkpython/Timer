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
        self.english_voice_id = None  # 存储英文语音ID[3,6](@ref)

    def get_english_voice(self):
        """获取系统可用的英文语音"""
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        for voice in voices:
            # 优先选择Zira（Windows英文语音）或包含"English"的语音[3,7](@ref)
            if "Zira" in voice.name or "English" in voice.name:
                return voice.id
        return voices[0].id if voices else None  # 默认返回第一个可用语音

    def speak(self, text):
        """英文语音播报（异步方式）"""

        def _speak():
            try:
                engine = pyttsx3.init()
                engine.setProperty('rate', 160)  # 稍快语速适合英文[6](@ref)
                engine.setProperty('volume', 0.8)
                
                # 设置英文语音（如果未初始化则先获取）
                if self.english_voice_id is None:
                    self.english_voice_id = self.get_english_voice()
                if self.english_voice_id:
                    engine.setProperty('voice', self.english_voice_id)
                
                engine.say(text)
                engine.runAndWait()
                engine.stop()
            except Exception as e:
                print(f"Speech synthesis failed: {e}")

        threading.Thread(target=_speak, daemon=True).start()

    def format_time_announcement(self, total_seconds):
        """将秒数转换为英文时间播报文本"""
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        
        # 处理英文单复数形式[8](@ref)
        if minutes > 0:
            minute_str = "minute" if minutes == 1 else "minutes"
            if seconds > 0:
                second_str = "second" if seconds == 1 else "seconds"
                return f"{minutes} {minute_str} and {seconds} {second_str}"
            return f"{minutes} {minute_str}"
        return f"{seconds} seconds" if seconds != 1 else "1 second"

    def voice_announce(self):
        """每10秒语音播报一次（英文）"""
        counter = 0
        while self.timer_running and not self.stop_voice:
            time.sleep(1)
            counter += 1

            if counter >= 10 and self.timer_running and not self.stop_voice:
                elapsed = int(time.time() - self.start_time)
                time_str = self.format_time_announcement(elapsed)
                
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Elapsed: {time_str}")
                self.speak(time_str)
                counter = 0

    def start_timer(self):
        """开始计时（英文提示）"""
        if self.voice_thread and self.voice_thread.is_alive():
            self.stop_voice = True
            self.voice_thread.join(timeout=1)

        self.start_time = time.time()
        self.timer_running = True
        self.stop_voice = False

        print(f"[{datetime.now().strftime('%H:%M:%S')}] Timer started!")
        self.speak("Timer started")

        self.voice_thread = threading.Thread(target=self.voice_announce, daemon=True)
        self.voice_thread.start()

    def stop_timer(self):
        """停止计时（英文提示）"""
        if self.timer_running:
            self.timer_running = False
            self.stop_voice = True

            elapsed = int(time.time() - self.start_time)
            time_str = self.format_time_announcement(elapsed)
            
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Timer stopped! Total: {time_str}")
            self.speak(f"Timer stopped. Total time: {time_str}")

    def run(self):
        """主运行循环（英文界面）"""
        print("=== Voice Timer (English) ===")
        print("Press Enter to start/restart timer")
        print("Type 'q' and press Enter to exit")
        print("Time announcements every 10 seconds")
        print("-" * 40)

        try:
            while True:
                user_input = input().strip().lower()

                if user_input == 'q':
                    if self.timer_running:
                        self.stop_timer()
                    print("Program exiting")
                    break
                else:
                    self.start_timer()

        except KeyboardInterrupt:
            print("\nProgram interrupted")
            if self.timer_running:
                self.stop_timer()


def main():
    try:
        import pyttsx3
    except ImportError:
        print("Error: pyttsx3 library required")
        print("Please install with: pip install pyttsx3")
        return

    # Windows系统可能需要额外依赖[4](@ref)
    try:
        import win32com.client
    except ImportError:
        print("Note: For better Windows support, install pypiwin32")
        print("Command: pip install pypiwin32")

    timer = VoiceTimer()
    timer.run()


if __name__ == "__main__":
    main()

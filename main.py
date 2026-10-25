import tkinter as tk
import subprocess

def main():
    CHROME_PATH="C:\Program Files\Google\Chrome\Application\chrome.exe"
    SESSION_DURATION_SECONDS = 30
    app = tk.Tk()

    app.title("VigilTime")
    app.geometry("500x350")

    title = tk.Label(
        app,
        text = "VigilTime",
        font = ("Arial",28,"bold")
    )
    title.pack(pady=30)

    timer_label = tk.Label(
        app,
        text = f"{SESSION_DURATION_SECONDS // 60:02d}:{SESSION_DURATION_SECONDS %60:02d}",
        font = ("Arial",36,"bold")
    )
    timer_label.pack(pady=20)

    def countdown(seconds,browser_process):
        minutes = seconds // 60
        remaining_seconds = seconds%60

        timer_label.config(
            text = f"{minutes:02d}:{remaining_seconds:02d}"
        )

        if seconds > 0:
            app.after(
                1000,
                countdown,
                seconds - 1,
                browser_process
            )
        else:
               #browser_process.terminate()
                subprocess.run(
                    ["taskkill","/PID",str(browser_process.pid),"/T","/F"],
                    capture_output=True,
                    text=True
                ) 
    def start_session():
        browser_process = subprocess.Popen([
            CHROME_PATH,
            r"--user-data-dir=C:\temp\vigiltime_chrome"
            "--new-window",
            "https://www.youtube.com"
        ])

        countdown(SESSION_DURATION_SECONDS,browser_process)

    start_button = tk.Button(
        app,
        text = f"START SESSION",
        font = ("Arial",14),
        command = start_session
    )
    start_button.pack(pady=20)

    app.mainloop()

#    subtitle = tk.Label(
#        app,
#        text = "Entertainment, on your time",
#        font = ("Arial",14)
#    )
#    subtitle.pack()

if __name__ == "__main__":
    main()

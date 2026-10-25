import json
import tkinter as tk
import subprocess


def main():

    with open("config.json","r") as file:
        config = json.load(file)

    APP_TITLE = config["app"]["title"]
    WINDOW_WIDTH = config["app"]["window_width"]
    WINDOW_HEIGHT = config["app"]["window_height"]

    CHROME_PATH = config["browser"]["executable_path"]
    PROFILE_PATH = config["browser"]["profile_path"]
    START_URL = config["browser"]["start_url"]

    SESSION_DURATION_SECONDS = config["session"]["duration_seconds"]
    app = tk.Tk()

    app.title(APP_TITLE)
    app.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")

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
            f"--user-data-dir={PROFILE_PATH}",
            "--new-window",
            START_URL
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

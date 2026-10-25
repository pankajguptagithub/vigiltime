import json
import tkinter as tk
import subprocess

def countdown(app,timer_label,seconds,browser_process):
    minutes = seconds // 60
    remaining_seconds = seconds%60

    timer_label.config(
        text = f"{minutes:02d}:{remaining_seconds:02d}"
    )

    if seconds > 0:
        app.after(
            1000,
            countdown,
            app,
            timer_label,
            seconds - 1,
            browser_process
        )
    else:
            subprocess.run(
                [
                    "taskkill","/PID",str(browser_process.pid),"/T","/F"
                ],
                capture_output=True,
                text=True
            ) 
def start_session(app,timer_label,config,selected_duration):
    selected_minutes = selected_duration.get()
    session_seconds = selected_minutes * 60

    browser_process = subprocess.Popen([
        config["browser"]["executable_path"],
        f'--user-data-dir={config["browser"]["profile_path"]}',
        "--new-window",
        config["browser"]["start_url"]
    ])

    countdown(
            app,
            timer_label,
            session_seconds,
            browser_process
    )

#    start_button = tk.Button(
#        app,
#        text = f"START SESSION",
#        font = ("Arial",14),
#        command = start_session
#    )
#    start_button.pack(pady=20)
#
#    app.mainloop()

def main():

    with open("config.json","r") as file:
        config = json.load(file)
    
    app = tk.Tk()
    app.title(config["app"]["title"])
    app.geometry(
        f'{config["app"]["window_width"]}x'
        f'{config["app"]["window_height"]}'
    )

    title = tk.Label(
        app,
        text=config["app"]["title"],
        font = ("Arial",28,"bold")
    )
    title.pack(pady=25)

    selected_duration = tk.IntVar(
        value=config["session"]["default_duration_in_mins"]
    )

    duration_frame = tk.Frame(app)
    duration_frame.pack(pady=10)

    for duration in config["session"]["duration_options_in_mins"]:
        duration_button = tk.Radiobutton(
            duration_frame,
            text=f"{duration}min",
            variable=selected_duration,
            value=duration,
        )
        duration_button.pack(
            side=tk.LEFT,
            padx=5
        )

    default_duration = config["session"]["default_duration_in_mins"]

    timer_label = tk.Label(
        app,
        text = f"{default_duration:02d}:00",
        font = ("Arial",36,"bold")
    )
    timer_label.pack(pady=20)

    def update_timer_display(*args):
        timer_label.config(
            text=f"{selected_duration.get():02d}:00"
        )

    selected_duration.trace_add(
        "write",
        update_timer_display
    )

    start_button = tk.Button(
        app,
        text = "START SESSION",
        font = ("Arial",14),
        command = lambda: start_session(
            app,
            timer_label,
            config,
            selected_duration
        )
    )
    start_button.pack(pady=20)
    app.mainloop()

if __name__ == "__main__":
    main()

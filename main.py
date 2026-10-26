import ctypes
import os
import sys
import json
import tkinter as tk
import subprocess

from ctypes import wintypes
from functools import partial

import psutil

WM_CLOSE = 0X0010

ENUM_WINDOWS_CALLBACK = ctypes.WINFUNCTYPE(
    ctypes.c_bool,
    wintypes.HWND,
    wintypes.LPARAM
)

def get_config_path():
    if getattr(sys, "frozen",False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))

    return os.path.join(
        base_path,
        "config.json"
    )

def load_config():
    with open(
        get_config_path(),
        "r",
        encoding = "utf-8"
    ) as file:
        return json.load(file)


def get_profile_path(config):
    configured_path = config["browser"]["profile_path"]

    return os.path.expandvars(configured_path)

def get_process_tree(process_id):
    try:
        root_process = psutil.Process(process_id)

        process_tree = root_process.children(
            recursive=True
        )

        process_tree.append(root_process)

        return process_tree

    except psutil.NoSuchProcess:
        return []

def close_chrome_window(window_handle,process_ids_pointer):
    window_process_id = wintypes.DWORD()

    ctypes.windll.user32.GetWindowThreadProcessId(
        window_handle,
        ctypes.byref(window_process_id)
    )

    process_ids = ctypes.cast(
        process_ids_pointer,
        ctypes.POINTER(ctypes.py_object)
    ).contents.value

    if window_process_id.value in process_ids:
        ctypes.windall.user32.PostMessageW(
            window_handle,
            WM_CLOSE,
            0,
            0
        )
    return true

def request_graceful_browser_close(process_ids):
    process_ids_object = ctypes.py_object(process_ids)

    process_ids_pointer = ctypes.cast(
        ctypes.pointer(process_ids_object),
        wintypes.LPARAM
    )

    callback = ENUM_WINDOWS_CALLBACK(
        close_chrome_window
    )

    ctypes.windll.user32.EnumWindows(
        callback,
        process_ids_pointer
    )

def force_kill_browser(browser_process):
    subprocess.run(
        [
            "taskkill",
            "/PID",
            str(browser_process.pid),
            "/T",
            "/F"
        ],
        capture_output=True,
        text=True,
        creationflags=subprocess.CREATE_NO_WINDOW
    )

def close_browser(browser_process,config):
    process_tree = get_process_tree(
        browser_process.pid
    )

    if not process_tree:
        return

    process_ids = {
        process.pid
        for process in process_tree
        if process.is_running()
    }

    request_graceful_browser_close(
        process_ids
    )

    shutdown_timeout = config["browser"][ 
        "graceful_shutdown_timeout_seconds"
    ]

    _, still_running = psutil.wait_procs(
        process_tree,
        timeout = shutdown_timeout
    )

    force_kill_enabled = config["browser"][
        force_kill_browser(browser_process)
        ]

    if still_running and force_kill_enabled:
        force_kill_browser(browser_process)

def countdown(
    app,
    timer_label,
    start_button,
    seconds,
    browser_process,
    config
):
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
            start_button,
            seconds - 1,
            browser_process,
            config
        )
    else: 
        close_browser(
            browser_process,
            config
        )

        timer_label.config(
            text = "SESSION ENDED"
        )

        start_button.config(
            state = tk.NORMAL
        )


def start_session(
        app,
        timer_label,
        start_button,
        config,
        selected_duration
):
    selected_minutes = selected_duration.get()
    session_seconds = selected_minutes * 60

    profile_path = get_profile_path(config)

    os.makedirs(
            profile_path,
            exist_ok=True
    )

    browser_process = subprocess.Popen([
        config["browser"]["executable_path"],
        f'--user-data-dir={config["browser"]["profile_path"]}',
        "--new-window",
        config["browser"]["start_url"]
    ])

    start_button.config(
        state = tk.DISABLED
    )

    countdown(
            app,
            timer_label,
            start_button,
            session_seconds,
            browser_process,
            config
    )

def update_timer_display(
    timer_label,
    selected_duration
):

    selected_minutes = selected_duration.get()

    timer_label.config(
        text = f"{selected_minutes:02d}:00"
    )

def create_duration_buttons(
    duration_frame,
    timer_label,
    selected_duration,
    allowed_durations,
):

    for duration in allowed_durations:
        duration_button = tk.Radiobutton(
            duration_frame,
            text = f"{duration}min",
            variable = selected_duration,
            value = duration,
            command = partial(
                update_timer_display,
                timer_label,
                selected_duration
            )
        )

        duration_button.pack(
            side = tk.LEFT,
            padx = 5
        )

def main():

    config = load_config()

    app = tk.Tk()

    app.title(
        config["app"]["title"]
    )

    app.geometry(
        f'{config["app"]["window_width"]}x'
        f'{config["app"]["window_height"]}'
    )

    app.resizable(
        False,
        False
    )

    title = tk.Label(
        app,
        text=config["app"]["title"],
        font=("Arial",28,"bold")
    )

    title.pack(
        pady=25
    )

    default_duration = config["session"][
        "default_duration_in_mins"
    ]

    selected_duration = tk.IntVar(
        value = default_duration
    )

    duration_frame = tk.Frame(app)

    duration_frame.pack(
        pady = 10
    )

    timer_label = tk.Label(
        app,
        text = f"{default_duration:02d}:00",
        font = ("Arial",36,"bold")
    )

    timer_label.pack(
        pady = 20
    )

    create_duration_buttons(
        duration_frame,
        timer_label,
        selected_duration,
        config["session"]["duration_options_in_mins"]

    )

    start_button = tk.Button(
        app,
        text = "START SESSION",
        font = ("Arial",14)
    )

    start_button.config(
        command = partial(
            start_session,
            app,
            timer_label,
            start_button,
            config,
            selected_duration
        )
    )

    start_button.pack(
        pady = 20
    )

    app.mainloop()

if __name__ == "__main__":
    main()

import py_positron as positron
import time

def main(ui):
    button = ui.document.getElementById("button")
    def on_click():
        current_time = time.strftime("%H:%M:%S")
        ui.document.alert(f"The current time is {current_time}")
    button.addEventListener("click", on_click)

def after_close(ui):
    print("Closed!")

positron.openUI("frontend/index.html", main, after_close, title="Example App")

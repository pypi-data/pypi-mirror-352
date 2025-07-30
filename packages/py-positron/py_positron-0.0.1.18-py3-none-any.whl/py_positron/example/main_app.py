import py_positron as main
import time

# Create the UI window (runs on a background event-loop thread)
ui = main.openUI("frontend/index.html")
button = ui.document.getElementById("button")
def on_click():
    current_time = time.strftime("%H:%M:%S")
    ui.document.alert(f"The current time is {current_time}")
button.addEventListener("click", on_click) # Add click event listener to the button
# Wait for the UI to close
ui.thread.join()
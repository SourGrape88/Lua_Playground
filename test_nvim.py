import pynvim
import time

# Attach to Neovim child process
nvim = pynvim.attach("child", argv=[
    r"C:\Users\Owner\scoop\apps\neovim\current\bin\nvim.exe",
    "--embed",
    "-u", r"C:\Users\Owner\Desktop\Projects\Lua_Playground\nvim_config\init_min.lua"
])

# Send some commands
nvim.ui_attach(40, 120, rgb=True)
nvim.command("enew")
nvim.command('call append(0, "Hello from Python!")')

# Use async_call to trigger a redraw
nvim.async_call(lambda nvim: nvim.command("redraw!"))

# Wait for redraw messages
while True:
    try:
        msg = nvim.next_message(timeout=0.1)  # use timeout only in PyNvim >=0.4.0
        if msg is None:
            continue
        print("Message received:", msg)
        if msg[0] == "redraw":
            print("Redraw event received!")
            break
    except TypeError:
        # Older PyNvim doesn't support timeout
        msg = nvim.next_message()
        if msg and msg[0] == "redraw":
            print("Redraw event received!")
            break
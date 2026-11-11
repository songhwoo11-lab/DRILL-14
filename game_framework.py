import time
running = False
stack = []


def change_mode(mode):
    if stack:
        stack.pop().finish()
    stack.append(mode)
    mode.init()


def push_mode(mode):
    if stack:
        stack[-1].pause()
    stack.append(mode)
    mode.init()


def pop_mode():
    if stack:
        stack.pop().finish()
    if stack:
        stack[-1].resume()
    else:
        quit()


def quit():
    global running
    running = False

frame_time = 0.0

def run(start_mode):
    global running, stack
    running = True
    stack = [start_mode]
    try:
        start_mode.init()

        global frame_time
        current_time = time.perf_counter()
        while running:
            frame_start = time.perf_counter()
            frame_time = max(0.0, frame_start - current_time)
            current_time = frame_start
            stack[-1].handle_events()
            stack[-1].update()
            stack[-1].render()
    finally:
        while stack:
            stack.pop().finish()
        running = False

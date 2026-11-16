import json
import math
import os
import queue
import threading
from pathlib import Path
from time import monotonic

import paho.mqtt.client as mqtt


GAMES = int(os.getenv("GAMES", "15"))
GAME_MOVES = [0, 1, 0, 1, 0, 1, 0]
QUIET_SECONDS = 0.250
TIMEOUT_SECONDS = 10
RESULTS_FILE = Path("/tmp/c2_bench.json")
BROKERS = ("connector-model", "connector-controller", "connector-artist", "connector-layout")

CLICK = "c2/connector-layout/layout_manager/bottom_domain/requests/request_click"
BOARD = "c2/connector-model/board/bottom_domain/notifications/notify_state_change"
STATUS = "c2/connector-model/status/bottom_domain/notifications/notify_status_change"
RESULT = "c2/connector-controller/board_logic/bottom_domain/notifications/notify_result_change"
events = queue.Queue()


def on_connect(client, userdata, flags, reason_code, properties):
    host, ready = userdata
    client.subscribe(f"c2/{host}/#")


def on_subscribe(client, userdata, mid, reason_codes, properties):
    host, ready = userdata
    ready.set()


def on_message(client, userdata, message):
    if message.topic.endswith(("/notify_next_tick", "/request_hover")):
        return
    events.put((monotonic(), message.topic, message.payload))


def receive(deadline):
    try:
        return events.get_nowait()
    except queue.Empty:
        pass
    remaining = deadline - monotonic()
    if remaining <= 0:
        raise queue.Empty
    return events.get(timeout=remaining)


def click(client, name):
    started = monotonic()
    client.publish(CLICK, json.dumps({"name": name}))
    return started


def wait_for_game(client, reset=False):
    click(client, "reset_scores" if reset else "new_game")
    deadline = monotonic() + TIMEOUT_SECONDS
    board_ready = reset
    status_ready = False
    while monotonic() < deadline:
        try:
            received, topic, payload = receive(deadline)
        except queue.Empty:
            break
        if topic == BOARD and not reset:
            board_ready = json.loads(payload) == [[0] * 7] * 6
        elif topic == STATUS:
            status = json.loads(payload)
            if reset:
                status_ready = not status["is_game_running"]
            else:
                status_ready = (
                    status["is_game_running"]
                    and status["current_player"] == 1
                    and status["turn_seconds_remaining"] is not None
                )
        if board_ready and status_ready:
            wait_for_quiet()
            return
    raise TimeoutError("Timed out waiting for game reset/start")


def wait_for_quiet():
    deadline = monotonic() + TIMEOUT_SECONDS
    last_message = monotonic()
    while monotonic() < deadline:
        try:
            received, topic, payload = receive(min(deadline, last_message + QUIET_SECONDS))
            last_message = max(last_message, received)
        except queue.Empty:
            if monotonic() >= last_message + QUIET_SECONDS:
                return
    raise TimeoutError("Timed out waiting for 250 ms of quiet")


def measure_move(client, move, column):
    player = 1 if move % 2 == 0 else -1
    row = 5 - move // 2
    sample = {"placed_ms": None, "turn_ms": None, "win_ms": None, "messages": 0}
    started = click(client, f"cell_{row}_{column}")
    deadline = started + TIMEOUT_SECONDS
    last_message = started
    game_ended = False
    completed = False
    while monotonic() < deadline:
        until = min(deadline, last_message + QUIET_SECONDS) if completed else deadline
        try:
            received, topic, payload = receive(until)
        except queue.Empty:
            if completed and monotonic() >= last_message + QUIET_SECONDS:
                return sample
            break
        if received < started:
            continue
        sample["messages"] += 1
        last_message = max(last_message, received)
        elapsed_ms = round((received - started) * 1000, 2)
        if topic == BOARD and sample["placed_ms"] is None:
            if json.loads(payload)[row][column] == player:
                sample["placed_ms"] = elapsed_ms
        elif topic == STATUS:
            status = json.loads(payload)
            if (sample["turn_ms"] is None
                and status["is_game_running"]
                and status["current_player"] == -player
                and status["turn_seconds_remaining"] is not None
            ):
                sample["turn_ms"] = elapsed_ms
            game_ended = not status["is_game_running"] and status["outcome"] == "red"
        elif topic == RESULT and sample["win_ms"] is None:
            if json.loads(payload)["result"] == "red":
                sample["win_ms"] = elapsed_ms
        if move == len(GAME_MOVES) - 1:
            completed = sample["placed_ms"] is not None and sample["win_ms"] is not None and game_ended
        else:
            completed = sample["placed_ms"] is not None and sample["turn_ms"] is not None
    raise TimeoutError(f"Move {move + 1} did not finish: {sample}")


def summarize(samples):
    summary = {}
    for key in ("placed_ms", "turn_ms", "win_ms", "messages"):
        values = []
        for sample in samples:
            if sample[key] is not None:
                values.append(sample[key])
        values.sort()
        summary[key] = {
            "count": len(values),
            "median": values[math.ceil(len(values) * 0.5) - 1],
            "p95": values[math.ceil(len(values) * 0.95) - 1],
        }
    return summary


def main():
    clients = {}
    samples = []
    try:
        for host in BROKERS:
            ready = threading.Event()
            client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, userdata=(host, ready))
            clients[host] = client
            client.on_connect = on_connect
            client.on_subscribe = on_subscribe
            client.on_message = on_message
            client.connect(host, 1883)
            client.loop_start()
            if not ready.wait(TIMEOUT_SECONDS):
                raise TimeoutError(f"Could not subscribe to {host}")
        layout = clients["connector-layout"]
        wait_for_game(layout, reset=True)
        for iii in range(GAMES):
            wait_for_game(layout)
            for jjj, column in enumerate(GAME_MOVES):
                sample = measure_move(layout, jjj, column)
                samples.append(sample)
            print(f"Game {iii + 1}/{GAMES} finished", flush=True)
        summary = summarize(samples)
        RESULTS_FILE.write_text(json.dumps({"samples": samples, "summary": summary}, indent=2) + "\n")
        print(f"C2 move benchmark ({GAMES} games)")
        print("Times start immediately before publishing the LayoutManager click request.")
        print(json.dumps(summary, indent=2))
        print(f"Results: {RESULTS_FILE}")
    finally:
        for client in clients.values():
            client.disconnect()
            client.loop_stop()


if __name__ == "__main__":
    main()

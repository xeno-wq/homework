"""
╔══════════════════════════════════════════════════════╗
║  ДЖАРВИС v3 — GPT-мозг + управление компьютером     ║
║                                                      ║
║  Установка зависимостей:                             ║
║  pip install openai edge-tts pygame                  ║
║       speechrecognition pyaudio pyautogui            ║
║                                                      ║
║  Вставь свой OpenAI API ключ в OPENAI_API_KEY ниже   ║
╚══════════════════════════════════════════════════════╝
"""

import os
import re
import json
import asyncio
import tempfile
import threading
import datetime
import webbrowser

import pyautogui
import pygame
import edge_tts
import speech_recognition as sr
from openai import OpenAI

# ──────────────────────────────────────────────────────
#  КОНФИГ — заполни эти поля
# ──────────────────────────────────────────────────────
OPENAI_API_KEY = "sk-..."          # ← вставь свой ключ сюда
GPT_MODEL      = "gpt-4o-mini"    # gpt-4o если хочешь умнее (дороже)

VOICE = "ru-RU-DmitryNeural"      # глубокий мужской голос
RATE  = "-5%"
PITCH = "-10Hz"

pyautogui.FAILSAFE = True          # движение мышью в угол = экстренная остановка
pyautogui.PAUSE    = 0.3           # пауза между действиями (секунд)

# ──────────────────────────────────────────────────────
#  ИНИЦИАЛИЗАЦИЯ
# ──────────────────────────────────────────────────────
client = OpenAI(api_key=OPENAI_API_KEY)
pygame.mixer.init()

# История диалога для GPT (даёт ему память разговора)
conversation_history: list[dict] = []

# ──────────────────────────────────────────────────────
#  ИНСТРУМЕНТЫ — то что GPT может вызвать
# ──────────────────────────────────────────────────────
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "open_application",
            "description": "Открыть приложение или сайт на компьютере пользователя",
            "parameters": {
                "type": "object",
                "properties": {
                    "target": {
                        "type": "string",
                        "description": "Название приложения (chrome, notepad, calculator, explorer) или URL сайта"
                    }
                },
                "required": ["target"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "type_text",
            "description": "Напечатать текст в активном окне (как будто пользователь набирает на клавиатуре)",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Текст для ввода"}
                },
                "required": ["text"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "press_key",
            "description": "Нажать клавишу или комбинацию (например enter, ctrl+c, alt+f4, win)",
            "parameters": {
                "type": "object",
                "properties": {
                    "key": {"type": "string", "description": "Клавиша или комбинация через +"}
                },
                "required": ["key"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "take_screenshot",
            "description": "Сделать скриншот экрана и сохранить его на рабочий стол",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "move_mouse",
            "description": "Переместить мышь и/или кликнуть в заданную точку экрана",
            "parameters": {
                "type": "object",
                "properties": {
                    "x":     {"type": "integer", "description": "X координата"},
                    "y":     {"type": "integer", "description": "Y координата"},
                    "click": {"type": "boolean", "description": "Кликнуть после перемещения?"}
                },
                "required": ["x", "y"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "scroll",
            "description": "Прокрутить страницу вверх или вниз",
            "parameters": {
                "type": "object",
                "properties": {
                    "direction": {
                        "type": "string",
                        "enum": ["up", "down"],
                        "description": "Направление прокрутки"
                    },
                    "amount": {"type": "integer", "description": "Количество прокруток (по умолч. 3)"}
                },
                "required": ["direction"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_time",
            "description": "Получить текущее время и дату",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "volume_control",
            "description": "Изменить громкость системы",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["up", "down", "mute"],
                        "description": "Действие с громкостью"
                    }
                },
                "required": ["action"]
            }
        }
    }
]

# ──────────────────────────────────────────────────────
#  ИСПОЛНЕНИЕ ИНСТРУМЕНТОВ
# ──────────────────────────────────────────────────────
def run_tool(name: str, args: dict) -> str:
    """Выполняет инструмент и возвращает строку-результат для GPT."""

    if name == "open_application":
        target = args["target"].lower()
        url_pattern = re.compile(r"https?://|www\.|\.com|\.ru|\.org")

        if url_pattern.search(target):
            url = target if target.startswith("http") else "https://" + target
            webbrowser.open(url)
            return f"Открыл сайт {url}"
        else:
            app_map = {
                "chrome":      "start chrome",
                "браузер":     "start chrome",
                "notepad":     "start notepad",
                "блокнот":     "start notepad",
                "calculator":  "start calc",
                "калькулятор": "start calc",
                "explorer":    "start explorer",
                "проводник":   "start explorer",
                "paint":       "start mspaint",
                "word":        "start winword",
                "excel":       "start excel",
            }
            cmd = app_map.get(target, f"start {target}")
            os.system(cmd)
            return f"Открыл приложение: {target}"

    elif name == "type_text":
        text = args["text"]
        pyautogui.write(text, interval=0.05)
        return f"Напечатал: {text}"

    elif name == "press_key":
        key_combo = args["key"].lower()
        keys = key_combo.split("+")
        if len(keys) == 1:
            pyautogui.press(keys[0].strip())
        else:
            pyautogui.hotkey(*[k.strip() for k in keys])
        return f"Нажал клавишу: {key_combo}"

    elif name == "take_screenshot":
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        filename = f"screenshot_{datetime.datetime.now().strftime('%H%M%S')}.png"
        path = os.path.join(desktop, filename)
        screenshot = pyautogui.screenshot()
        screenshot.save(path)
        return f"Скриншот сохранён: {path}"

    elif name == "move_mouse":
        x, y = args["x"], args["y"]
        click = args.get("click", False)
        pyautogui.moveTo(x, y, duration=0.5)
        if click:
            pyautogui.click()
        return f"Переместил мышь в ({x}, {y})" + (" и кликнул" if click else "")

    elif name == "scroll":
        direction = args["direction"]
        amount = args.get("amount", 3)
        pyautogui.scroll(amount if direction == "up" else -amount)
        return f"Прокрутил {'вверх' if direction == 'up' else 'вниз'} на {amount}"

    elif name == "get_time":
        now = datetime.datetime.now()
        return now.strftime("Сейчас %H:%M, %d %B %Y года")

    elif name == "volume_control":
        action = args["action"]
        if action == "up":
            pyautogui.press("volumeup")
        elif action == "down":
            pyautogui.press("volumedown")
        elif action == "mute":
            pyautogui.press("volumemute")
        return f"Громкость: {action}"

    return "Инструмент выполнен"


# ──────────────────────────────────────────────────────
#  GPT — отправка сообщения и получение ответа
# ──────────────────────────────────────────────────────
SYSTEM_PROMPT = """Ты — Джарвис, голосовой ИИ-ассистент пользователя.
Говори кратко, уверенно, как настоящий Джарвис из фильма про Железного Человека.
Обращайся к пользователю «сэр».
Ты можешь управлять компьютером через инструменты — используй их когда нужно.
Когда пользователь просит что-то сделать на компьютере — сразу вызывай нужный инструмент без лишних вопросов.
Отвечай ТОЛЬКО на русском языке. Ответы короткие: 1-2 предложения максимум.
"""

def ask_gpt(user_message: str) -> str:
    """Отправляет сообщение в GPT, обрабатывает вызовы инструментов, возвращает финальный текст."""

    conversation_history.append({"role": "user", "content": user_message})
    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + conversation_history

    response = client.chat.completions.create(
        model=GPT_MODEL,
        messages=messages,
        tools=TOOLS,
        tool_choice="auto"
    )

    msg = response.choices[0].message

    # Цикл обработки инструментов (GPT может вызвать несколько подряд)
    while msg.tool_calls:
        tool_results = []

        for tool_call in msg.tool_calls:
            fn_name = tool_call.function.name
            fn_args = json.loads(tool_call.function.arguments)

            print(f"🔧 Инструмент: {fn_name}({fn_args})")
            result = run_tool(fn_name, fn_args)
            print(f"   ✓ {result}")

            tool_results.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result
            })

        conversation_history.append(msg)
        conversation_history.extend(tool_results)
        messages = [{"role": "system", "content": SYSTEM_PROMPT}] + conversation_history

        response = client.chat.completions.create(
            model=GPT_MODEL,
            messages=messages,
            tools=TOOLS,
            tool_choice="auto"
        )
        msg = response.choices[0].message

    reply = msg.content or "Выполнено, сэр."
    conversation_history.append({"role": "assistant", "content": reply})

    # Ограничиваем историю (последние 40 сообщений)
    if len(conversation_history) > 40:
        conversation_history[:] = conversation_history[-40:]

    return reply


# ──────────────────────────────────────────────────────
#  TTS — озвучка
# ──────────────────────────────────────────────────────
async def _synthesize(text: str, path: str):
    communicate = edge_tts.Communicate(text, VOICE, rate=RATE, pitch=PITCH)
    await communicate.save(path)

def say(text: str):
    print(f"\n🤖 Джарвис: {text}")
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
        tmp_path = f.name

    asyncio.run(_synthesize(text, tmp_path))

    pygame.mixer.music.load(tmp_path)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

    pygame.mixer.music.unload()
    os.unlink(tmp_path)


# ──────────────────────────────────────────────────────
#  STT — распознавание голоса
# ──────────────────────────────────────────────────────
def listen() -> str:
    r = sr.Recognizer()
    r.energy_threshold = 300
    r.dynamic_energy_threshold = True

    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=0.8)
        print("\n🎙  Слушаю...")
        try:
            audio = r.listen(source, timeout=6, phrase_time_limit=8)
            text = r.recognize_google(audio, language="ru-RU").lower()
            print(f"👤 Вы: {text}")
            return text
        except sr.WaitTimeoutError:
            return ""
        except sr.UnknownValueError:
            return ""
        except sr.RequestError as e:
            print(f"[Ошибка Google STT]: {e}")
            return ""


# ──────────────────────────────────────────────────────
#  ГЛАВНЫЙ ЦИКЛ
# ──────────────────────────────────────────────────────
WAKE_WORDS = ("джарвис", "jarvis")
STOP_WORDS = ("пока", "отключись", "выключись", "стоп", "до свидания")

def main():
    say("Системы инициализированы. Связь с GPT установлена. Готов к работе, сэр.")
    print("\n💡 Примеры команд:")
    print("   «Открой ютуб»")
    print("   «Сделай скриншот»")
    print("   «Напечатай привет мир»")
    print("   «Нажми ctrl+c»")
    print("   «Который час?»")
    print("   «Сделай потише»\n")

    while True:
        raw = listen()

        if not raw:
            continue

        command = raw
        for ww in WAKE_WORDS:
            command = command.replace(ww, "").strip()

        if not command:
            say("Слушаю вас, сэр.")
            continue

        if any(w in command for w in STOP_WORDS):
            say("До свидания, сэр. Отключаюсь.")
            break

        print("🧠 Думаю...")
        try:
            reply = ask_gpt(command)
            say(reply)
        except Exception as e:
            print(f"[Ошибка GPT]: {e}")
            say("Произошла ошибка при обращении к GPT, сэр.")


if __name__ == "__main__":
    main()
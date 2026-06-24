import json
import os
import random
import threading
import time
from collections import deque

import requests
from dotenv import load_dotenv

load_dotenv()

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
GEMINI_RPM_LIMIT = 5
GEMINI_RPD_LIMIT = 20
REQUEST_TIMEOUT_SECONDS = 30
MAX_RETRY_ROUNDS = 2
RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}


class GeminiKeyRotator:
    def __init__(self) -> None:
        keys = [os.getenv(f"GEMINI_API_KEY{i}") for i in range(1, 7)]

        fallback_key = os.getenv("GEMINI_API_KEY")
        if fallback_key and fallback_key not in keys:
            keys.append(fallback_key)

        self._keys = [key for key in keys if key]
        self._minute_windows = {key: deque() for key in self._keys}
        self._day_windows = {key: deque() for key in self._keys}
        self._lock = threading.Lock()
        self._next_index = 0

    def is_ready(self) -> bool:
        return bool(self._keys)

    def get_keys_count(self) -> int:
        return len(self._keys)

    def acquire_key(self, excluded_keys: set[str] | None = None) -> str:
        if not self._keys:
            raise RuntimeError(
                "Nenhuma chave Gemini configurada. Defina GEMINI_API_KEY1 até "
                "GEMINI_API_KEY6."
            )

        excluded_keys = excluded_keys or set()

        while True:
            with self._lock:
                now = time.time()
                available_indexes = []

                for index, key in enumerate(self._keys):
                    if key in excluded_keys:
                        continue
                    self._prune(key, now)
                    if (
                        len(self._minute_windows[key]) < GEMINI_RPM_LIMIT
                        and len(self._day_windows[key]) < GEMINI_RPD_LIMIT
                    ):
                        available_indexes.append(index)

                if available_indexes:
                    chosen_index = self._pick_next_index(available_indexes)
                    key = self._keys[chosen_index]
                    self._minute_windows[key].append(now)
                    self._day_windows[key].append(now)
                    self._next_index = (chosen_index + 1) % len(self._keys)
                    return key

                sleep_seconds = self._next_wait_seconds(now)

            time.sleep(sleep_seconds)

    def _pick_next_index(self, available_indexes: list[int]) -> int:
        for offset in range(len(self._keys)):
            candidate = (self._next_index + offset) % len(self._keys)
            if candidate in available_indexes:
                return candidate
        return available_indexes[0]

    def _prune(self, key: str, now: float) -> None:
        minute_window = self._minute_windows[key]
        while minute_window and now - minute_window[0] >= 60:
            minute_window.popleft()

        day_window = self._day_windows[key]
        while day_window and now - day_window[0] >= 86400:
            day_window.popleft()

    def _next_wait_seconds(self, now: float) -> float:
        waits = []

        for key in self._keys:
            minute_window = self._minute_windows[key]
            day_window = self._day_windows[key]

            minute_wait = 0.0
            day_wait = 0.0

            if len(minute_window) >= GEMINI_RPM_LIMIT:
                minute_wait = max(0.0, 60 - (now - minute_window[0]))

            if len(day_window) >= GEMINI_RPD_LIMIT:
                day_wait = max(0.0, 86400 - (now - day_window[0]))

            waits.append(max(minute_wait, day_wait))

        return max(0.1, min(waits) if waits else 1.0)


KEY_ROTATOR = GeminiKeyRotator()

def load_prompt():
    prompt_path = os.path.join(os.path.dirname(__file__), "../prompts/gemini_prompt.txt")
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()


def is_configured() -> bool:
    return KEY_ROTATOR.is_ready()


def _mask_key(key: str) -> str:
    if len(key) <= 8:
        return "***"
    return f"{key[:6]}...{key[-4:]}"


def _extract_response_text(raw: dict) -> str:
    return raw["candidates"][0]["content"]["parts"][0]["text"]


def _parse_model_response(text: str, fallback_prompt: str) -> dict:
    cleaned_text = text.strip()

    if cleaned_text.startswith("```"):
        lines = cleaned_text.splitlines()
        if len(lines) >= 3:
            cleaned_text = "\n".join(lines[1:-1]).strip()

    try:
        return json.loads(cleaned_text)
    except json.JSONDecodeError:
        return {
            "security_risk": False,
            "issues": [],
            "safe_prompt": fallback_prompt,
            "error": "Resposta inválida do modelo externo",
        }


def _compute_backoff_seconds(attempt_number: int) -> float:
    base = min(2 ** (attempt_number - 1), 16)
    jitter = random.uniform(0.1, 0.9)
    return base + jitter


def _should_retry(exc: Exception) -> bool:
    if isinstance(exc, requests.exceptions.Timeout):
        return True

    if isinstance(exc, requests.exceptions.ConnectionError):
        return True

    if isinstance(exc, requests.exceptions.HTTPError) and exc.response is not None:
        return exc.response.status_code in RETRYABLE_STATUS_CODES

    return False


def _build_request_url(api_key: str) -> str:
    return (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"{GEMINI_MODEL}:generateContent?key={api_key}"
    )


def _build_payload(prompt: str) -> dict:
    system_prompt = load_prompt()
    return {
        "contents": [
            {
                "parts": [
                    {"text": f"{system_prompt}\n\nPrompt a analisar:\n{prompt}"}
                ]
            }
        ]
    }


def _request_with_key(prompt: str, api_key: str) -> dict:
    response = requests.post(
        _build_request_url(api_key),
        json=_build_payload(prompt),
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    response.raise_for_status()

    raw = response.json()
    text = _extract_response_text(raw)
    return _parse_model_response(text, prompt)


def analyze_security(sanitized_prompt: str) -> dict:
    if not is_configured():
        return {
            "security_risk": False,
            "issues": [],
            "safe_prompt": sanitized_prompt,
            "error": (
                "Nenhuma chave Gemini configurada. Defina GEMINI_API_KEY1 até "
                "GEMINI_API_KEY6."
            ),
        }

    attempted_keys: set[str] = set()
    last_exception: Exception | None = None
    max_attempts = max(KEY_ROTATOR.get_keys_count() * MAX_RETRY_ROUNDS, 1)

    for attempt_number in range(1, max_attempts + 1):
        if len(attempted_keys) == KEY_ROTATOR.get_keys_count():
            attempted_keys.clear()

        api_key = KEY_ROTATOR.acquire_key(excluded_keys=attempted_keys)
        attempted_keys.add(api_key)

        try:
            return _request_with_key(sanitized_prompt, api_key)
        except Exception as exc:
            last_exception = exc
            if not _should_retry(exc) or attempt_number == max_attempts:
                break

            wait_seconds = _compute_backoff_seconds(attempt_number)
            print(
                "Aviso: falha transitória no Gemini "
                f"(tentativa {attempt_number}/{max_attempts}, "
                f"chave={_mask_key(api_key)}): {type(exc).__name__}. "
                f"Nova tentativa em {wait_seconds:.1f}s."
            )
            time.sleep(wait_seconds)

    if isinstance(last_exception, requests.exceptions.HTTPError) and last_exception.response is not None:
        error_message = (
            f"HTTP {last_exception.response.status_code} ao consultar o Gemini "
            f"após {max_attempts} tentativas"
        )
    elif last_exception is not None:
        error_message = (
            f"{type(last_exception).__name__} ao consultar o Gemini após "
            f"{max_attempts} tentativas: {last_exception}"
        )
    else:
        error_message = "Falha desconhecida ao consultar o Gemini"

    return {
        "security_risk": False,
        "issues": [],
        "safe_prompt": sanitized_prompt,
        "error": error_message,
    }

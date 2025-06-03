## Product Requirements Document

### 1. Overview / Problem

Нужен минимальный бот-MVP, который по полученной локации мгновенно возвращает один необычный факт о ближайшем месте, используя OpenAI GPT-4.1-mini. В будущем — поддержка live-location.

### 2. Key User Flows

1. **Static Point**
   User → «Поделиться локацией» → Bot → факт (текст ≤ 280 симв.).
2. **Live Location (v1.1)**
   User → «Поделиться live-локацией 10 мин» → Bot → новый факт каждые 10 мин до завершения/остановки.

### 3. Functional Requirements

* Обрабатывать сообщения с `location`.
* Вызывать `chat.completions` (темп ≈ 0.8, макс 120 токенов) с промптом:
  «Given coords X,Y return one surprising fact about any landmark/event within 1 km».
* Отвечать фактом в том же чате.
* Переменные окружения: `TELEGRAM_TOKEN`, `OPENAI_API_KEY`.
* CI/CD: GitHub → Railway автодеплой main.
* (v1.1) Таск-шедулер: пока live-сессия активна — повторять запрос каждые 10 мин; завершать по `live_period` или `/stop`.

### 4. Non-Goals

* Хранение БД, аналитика и UI-кнопки.
* Поддержка групповых чатов, мультиязычность, детальные rate-limit стратегии.

### 5. Milestones & Release Plan

| Дата        | Этап                                                                    |
| ----------- | ----------------------------------------------------------------------- |
| **Сегодня** | Репо-скелет, PRD, `.env.example`.                                       |
| **+2 ч**    | MVP: парсинг `location`, ответ через OpenAI; тест локально.             |
| **+4 ч**    | Push в GitHub, Railway deploy, проверка в прод-чате → **Release v1.0**. |
| **+6 ч**    | Реализация live-loop, `/stop`, тест → **Release v1.1**.                 |

---


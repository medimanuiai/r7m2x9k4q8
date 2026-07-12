# Jyothishyam — AI Engine Specification

**Version:** 0.1 (Draft)
**Last Updated:** 2026-05-31
**Status:** 🟡 In Review
**Module:** `backend/ai_engine.py`
**Language:** Python 3.11+

---

## 1. Overview

The AI Engine is responsible for:
1. Building structured prompts from a user's birth chart context and question.
2. Calling the configured AI provider (OpenAI / Anthropic / Google).
3. Tracking token usage for billing.
4. Returning a structured answer with token counts.

The AI Engine is **stateless** — it does not access the database. Credit checking and response persistence are handled by higher-level services (credit_manager and the route layer).

---

## 2. Module Architecture

```
backend/
├── ai_engine.py            ← Main AI engine (provider-agnostic interface)
├── ai_providers/
│   ├── __init__.py
│   ├── base.py             ← Abstract AIProvider base class
│   ├── openai_provider.py  ← OpenAI implementation
│   ├── anthropic_provider.py ← Anthropic implementation
│   └── google_provider.py  ← Google Gemini implementation
└── prompt_builder.py       ← Prompt construction from chart context
```

---

## 3. Provider Configuration

Configured via environment variables:

| Variable | Default | Description |
|---|---|---|
| `AI_PROVIDER` | `openai` | Active provider: `openai`, `anthropic`, `google` |
| `AI_MODEL` | `gpt-4o-mini` | Model name (provider-specific) |
| `AI_MAX_TOKENS` | `1024` | Max completion tokens |
| `AI_TEMPERATURE` | `0.7` | Sampling temperature (0.0–1.0) |
| `OPENAI_API_KEY` | — | OpenAI API key |
| `ANTHROPIC_API_KEY` | — | Anthropic API key |
| `GOOGLE_API_KEY` | — | Google AI API key |

**Model Options:**

| Provider | Recommended Model | Budget Model |
|---|---|---|
| OpenAI | `gpt-4o` | `gpt-4o-mini` |
| Anthropic | `claude-3-5-sonnet-20241022` | `claude-3-haiku-20240307` |
| Google | `gemini-1.5-pro` | `gemini-1.5-flash` |

---

## 4. Core Types

```python
from pydantic import BaseModel
from enum import Enum

class QuestionType(str, Enum):
    GENERAL = "general"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    HOROSCOPE = "horoscope"
    COMPATIBILITY = "compatibility"

class AIRequest(BaseModel):
    question: str                    # User's raw question
    question_type: QuestionType
    chart_context: ChartContext      # Structured chart data
    user_name: str                   # For personalisation
    language: str = "en"             # Response language

class ChartContext(BaseModel):
    ascendant_sign: str
    ascendant_nakshatra: str
    sun_sign: str
    moon_sign: str
    planets: list[PlanetSummary]     # Key planet positions
    current_maha_dasha: str
    current_antar_dasha: str
    active_yogas: list[str]          # Names of active yogas only
    lagna_lord_sign: str             # Sign of lagna lord

class PlanetSummary(BaseModel):
    name: str
    sign: str
    house: int
    is_retrograde: bool
    dignity: str
    nakshatra: str

class AIResponse(BaseModel):
    answer: str                      # Full AI answer text
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    model_used: str
    provider: str
    latency_ms: int
```

---

## 5. `ai_engine.py` — Main Interface

### 5.1 Function: `ask_question`

**Purpose:** Primary entry point for all AI astrological queries.

**Signature:**
```python
async def ask_question(request: AIRequest) -> AIResponse
```

**Process:**
1. Build the system prompt using `prompt_builder.build_system_prompt()`.
2. Build the user message using `prompt_builder.build_user_message()`.
3. Select and instantiate the configured provider.
4. Call provider's `complete()` method.
5. Parse and return `AIResponse`.

**Error Handling:**
- `AIProviderError` on API failure → propagates as `AI_SERVICE_UNAVAILABLE`
- `AITimeoutError` if response exceeds 30 seconds
- Never expose raw API error messages to end users

---

## 6. `prompt_builder.py`

### 6.1 System Prompt Structure

The system prompt establishes the AI's persona, expertise scope, and output format.

**Template:**
```
You are Jyothish, an expert Vedic astrologer with deep knowledge of:
- Jyotisha Shastra (classical Vedic astrology)
- Parashari system of chart interpretation
- Vimshottari Dasha system
- Nakshatra analysis
- Yoga identification and interpretation
- Divisional charts (Divisional chart analysis)

You are helping {user_name} understand their birth chart and life patterns.

BIRTH CHART CONTEXT:
- Ascendant (Lagna): {ascendant_sign} ({ascendant_nakshatra} nakshatra)
- Sun: {sun_sign}
- Moon: {moon_sign}
- Lagna Lord: In {lagna_lord_sign}
- Current Mahadasha: {current_maha_dasha}
- Current Antardasha: {current_antar_dasha}
- Active Yogas: {active_yogas}

PLANET POSITIONS:
{planet_table}

RULES:
1. Answer only astrology-related questions. Politely decline off-topic requests.
2. Do not make absolute predictions — use probabilistic language ("likely", "indicates", "suggests").
3. Always connect your answer to specific planetary placements in the chart.
4. Be compassionate, positive where possible, and constructive about challenges.
5. Do not mention competitor astrology apps or services.
6. Response language: {language}
7. Keep responses clear and structured. Use paragraphs, not bullet points, for narrative flow.
```

### 6.2 User Message Templates

**`general` question:**
```
The user asks: "{question}"

Please provide a thoughtful Vedic astrological interpretation based on the chart provided.
Reference specific planetary placements, dashas, and yogas in your answer.
```

**`daily` prediction:**
```
Provide today's astrological guidance for {user_name}.
Today's date: {today_date}
Current transit highlights: {transit_summary}

Focus on: energy levels, opportunities, cautions, and an auspicious time window.
```

**`weekly` prediction:**
```
Provide a weekly astrological overview for {user_name}.
Week of: {week_start} to {week_end}

Cover: general themes, career/finance, relationships, health, and key dates to watch.
```

**`monthly` prediction:**
```
Provide a monthly astrological forecast for {user_name}.
Month: {month_name} {year}

Cover: monthly theme, major transit impacts on the natal chart, dasha influence, 
and key dates with high/low energy windows.
```

**`horoscope` full reading:**
```
Provide a comprehensive birth chart reading for {user_name}.

Cover in detail:
1. Personality and physical constitution (Lagna analysis)
2. Mind and emotions (Moon analysis)
3. Soul purpose and vitality (Sun analysis)
4. Career and public life (10th house + lord)
5. Relationships and marriage (7th house + Venus)
6. Wealth and resources (2nd house + Jupiter)
7. Current life phase (active Dasha interpretation)
8. Key yogas and their manifestation
9. Overall life themes and spiritual path
10. Actionable guidance for the current period
```

**`compatibility` analysis:**
```
Analyze the astrological compatibility between {person1_name} and {person2_name}.
Compatibility type: {compatibility_type}

Person 1 Chart Summary: {chart1_context}
Person 2 Chart Summary: {chart2_context}
Ashtakoot Score: {kuta_total}/36

Analyze:
1. Moon compatibility (emotional harmony)
2. Venus-Mars interaction (attraction/physical)
3. Jupiter compatibility (values, growth)
4. Saturn compatibility (long-term stability)
5. Dasha compatibility (timing alignment)
6. Overall assessment for {compatibility_type} relationship
7. Strengths and challenges
8. Practical guidance
```

---

## 7. `ai_providers/base.py` — Abstract Base Class

```python
from abc import ABC, abstractmethod

class AIProvider(ABC):
    
    @abstractmethod
    async def complete(
        self,
        system_prompt: str,
        user_message: str,
        max_tokens: int,
        temperature: float
    ) -> ProviderResponse:
        """Call the AI model and return a structured response."""
        ...
    
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return provider identifier string."""
        ...
    
    @property
    @abstractmethod
    def model_name(self) -> str:
        """Return model name string."""
        ...

class ProviderResponse(BaseModel):
    content: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    latency_ms: int
```

---

## 8. Provider Implementations

### 8.1 OpenAI (`openai_provider.py`)

```python
# Uses: openai Python SDK (async)
# Client: AsyncOpenAI
# Method: client.chat.completions.create()
# Message format: [{"role": "system", ...}, {"role": "user", ...}]
# Token extraction: response.usage.prompt_tokens / completion_tokens
```

### 8.2 Anthropic (`anthropic_provider.py`)

```python
# Uses: anthropic Python SDK (async)
# Client: AsyncAnthropic
# Method: client.messages.create()
# System goes in: messages.create(system=..., messages=[{"role": "user", ...}])
# Token extraction: response.usage.input_tokens / output_tokens
```

### 8.3 Google (`google_provider.py`)

```python
# Uses: google-generativeai Python SDK
# Client: genai.GenerativeModel
# Method: await model.generate_content_async()
# Token extraction: response.usage_metadata.prompt_token_count / candidates_token_count
```

---

## 9. Token → Credit Mapping

Token usage is tracked but does **not** directly determine credit cost. Credits are charged at a fixed rate per `question_type` (defined in credit_manager). Token tracking is for:
- Internal cost monitoring by the platform
- Admin analytics dashboards
- Future dynamic pricing if needed

**Platform cost estimation (for budgeting):**

| Model | Input (per 1M tokens) | Output (per 1M tokens) |
|---|---|---|
| gpt-4o-mini | $0.15 | $0.60 |
| gpt-4o | $2.50 | $10.00 |
| claude-3-haiku | $0.25 | $1.25 |
| claude-3-5-sonnet | $3.00 | $15.00 |
| gemini-1.5-flash | $0.075 | $0.30 |
| gemini-1.5-pro | $1.25 | $5.00 |

---

## 10. Safety & Security

### 10.1 Prompt Injection Prevention

User question text is sanitized before injection into prompts:
1. Strip leading/trailing whitespace.
2. Truncate to max 500 characters.
3. Detect and reject questions containing prompt injection patterns:
   - `ignore previous instructions`
   - `you are now`
   - `system:`, `<|im_start|>`, `[INST]`
   - Unusual Unicode control characters
4. Wrap user text in explicit delimiters: `"""user question: {sanitized_question}"""`

### 10.2 Content Filtering

- Never ask AI to make medical, legal, or financial decisions.
- If AI response contains any of the blocked phrases (configurable list), replace with a safe fallback.
- Log all flagged responses for admin review.

### 10.3 API Key Security

- Keys loaded only from environment variables — never hardcoded.
- Keys never logged or included in error responses.
- Rotate keys via environment variable update (no code change required).

---

## 11. Retry & Resilience

| Scenario | Behavior |
|---|---|
| API rate limit (429) | Retry with exponential backoff: 1s, 2s, 4s (max 3 retries) |
| Network timeout | Timeout after 30 seconds, raise `AITimeoutError` |
| API 5xx error | Retry once after 2 seconds |
| Invalid response format | Log and raise `AIProviderError` |
| Max retries exceeded | Return `AI_SERVICE_UNAVAILABLE` to user |

> Credits are **not** deducted if the AI call fails. Only deduct after a successful response is saved.

---

## 12. Open Decisions

| # | Decision | Options | Status |
|---|---|---|---|
| AI1 | Default AI provider | OpenAI (current) / Anthropic / Google | 🟡 Pending |
| AI2 | Async AI calls with job queue | Yes (Celery) / No (synchronous) | 🟡 Pending |
| AI3 | Response streaming | Yes / No (batch) | 🟡 Pending |
| AI4 | Language support | English only / Multi-language | 🟡 Pending |
| AI5 | AI response caching | Yes (Redis, by chart+question hash) / No | 🟡 Pending |
| AI6 | Content moderation layer | OpenAI Moderation API / Custom / None | 🟡 Pending |

---

*This document is a living specification. Sections marked 🟡 are pending decisions.*

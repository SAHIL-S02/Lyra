# Lyra — AI Architecture & Model Specification

> **Project:** Lyra  
> **Document:** `AI.md`  
> **Purpose:** Define every AI/model component used by Lyra, what it does, how it contributes to the assistant, and what it looks like in real-life usage.
>
> **Design principle:** Lyra is one assistant from the user's perspective, but internally it uses multiple specialized AI/model components.

---

# 1. The Big Picture

Lyra should **not** depend on one model for every task.

Instead, Lyra uses a model stack:

```text
                             ┌─────────────────┐
                             │      USER       │
                             │      "Hey Lyra" │
                             └────────┬────────┘
                                      │
                                      ▼
                             ┌─────────────────┐
                             │  Voice Layer    │
                             │ Wake Word + VAD │
                             └────────┬────────┘
                                      │
                                      ▼
                             ┌─────────────────┐
                             │   LYRA CORE     │
                             │ Session/Router  │
                             └────────┬────────┘
                                      │
                              ┌───────┴────────┐
                              │  Query Router  │
                              └───────┬────────┘
                                      │
              ┌───────────────────────┼────────────────────────┐
              │                       │                        │
              ▼                       ▼                        ▼
       ┌──────────────┐       ┌──────────────┐        ┌──────────────┐
       │  Local AI    │       │  Cloud Voice │        │  Tool/Agent  │
       │  Qwen3       │       │  Gemini Live │        │    Layer     │
       └──────┬───────┘       └──────┬───────┘        └──────┬───────┘
              │                      │                        │
              │                      │                 ┌──────┼───────┐
              │                      │                 ▼      ▼       ▼
              │                      │              Spotify  Web    Home
              │                      │                              │
              │                      │                            MQTT
              │                      │                              │
              │                      │                            ESP32
              └──────────────────────┼──────────────────────────────┘
                                     ▼
                              ┌──────────────┐
                              │    Memory    │
                              │     + RAG    │
                              └──────┬───────┘
                                     │
                                     ▼
                              Final response
                                     │
                                     ▼
                                   Voice
```

---

# 2. AI Components Used by Lyra

| Component | Main Job | Local/Cloud | Initial Choice |
|---|---|---|---|
| Wake-word model | Detect "Lyra" | Local | Dedicated wake-word engine |
| VAD | Detect speech/silence | Local | Dedicated VAD |
| Real-time voice model | Live conversation | Cloud | **Gemini 3.8 Live** |
| Local LLM | Offline conversation | Local | **Qwen3-1.7B** |
| Online reasoning model | Difficult/current tasks | Cloud | Gemini family / provider abstraction |
| Web search | Fresh information | Online | Search grounding / web tool |
| Embedding model | Semantic memory/RAG | Local/Cloud | Pluggable |
| Memory extractor | Extract useful memories | Local/Cloud | Small fast model |
| Summarizer | Hourly summaries | Local/Cloud | Fast text model |
| Personalization model | Learn response style | Local | Optional future fine-tuned model |
| Tool-calling layer | Execute actions | Application logic | Function/tool calling |
| TTS | Voice output if separated | Local/Cloud | Provider abstraction |

---

# 3. AI #1 — Wake Word Model

## Purpose

The wake-word model detects whether the user has called Lyra.

Example:

```text
Background:
TV playing
People talking
Fans running

User:
"Hey Lyra"

        ↓

Wake-word detector

        ↓

WAKE EVENT
```

## Why it should be local

Wake-word detection should run locally whenever possible.

Benefits:

- No continuous cloud audio upload
- Lower latency
- Lower API usage
- Better privacy
- Works even when the internet is down

## Responsibility

The wake-word model should **not** answer questions.

Its only job is:

```text
Did the user say the wake phrase?
            ↓
YES / NO
```

## Real-life example

```text
Lyra sleeping...

User:
"Hey Lyra"

Wake-word model:
TRUE

Lyra:
"Yes?"
```

---

# 4. AI #2 — Voice Activity Detection (VAD)

## Purpose

VAD determines whether the microphone currently contains human speech.

It helps Lyra detect:

```text
Speech started
Speech continues
Speech ended
```

## Why it matters

Without VAD, the assistant may:

- Stop listening too early
- Listen forever
- Send unnecessary audio
- Have poor conversation timing

## Real-life example

```text
User:
"Hey Lyra..."

     ↓

VAD detects speech

     ↓

User:
"...explain binary search to me."

     ↓

VAD detects end of speech

     ↓

Lyra processes request
```

## Important

VAD is **not an LLM**.

It is an audio/signal-processing component.

---

# 5. AI #3 — Gemini 3.8 Live

## Role in Lyra

This is the primary **real-time voice brain** for the cloud mode.

Google currently lists `gemini-3.8-live` as the default option for most low-latency voice-agent experiences. It supports audio input/output, function calling, search grounding, Live API sessions, and interleaved reasoning. The current documented input limit is 131,072 tokens and output limit is 65,536 tokens. citeturn293599search0turn293599search1

The Live API uses persistent WebSocket sessions and supports streaming audio input and native audio output. citeturn293599search5turn293599search2

## Responsibilities

Gemini Live can handle:

- Real-time conversation
- Understanding spoken requests
- Maintaining conversation context
- Natural voice responses
- Tool/function calls
- Search-grounded responses
- More complex reasoning
- Multilingual conversation

## Real-life example: Normal conversation

```text
User:
"Hey Lyra."

        ↓

Gemini Live

        ↓

Lyra:
"Yes? What can I do for you?"
```

Then:

```text
User:
"Explain neural networks."

        ↓

Gemini Live

        ↓

Lyra:
"A neural network is a machine-learning model
inspired by interconnected neurons..."
```

## Real-life example: Tool calling

```text
User:
"Lyra, play my study playlist."

        ↓

Gemini Live understands intent

        ↓

Tool Call:
spotify.play_playlist("study")

        ↓

Your backend

        ↓

Spotify
```

## Real-life example: Smart-home command

Later:

```text
User:
"Turn on my study room light."

        ↓

Gemini Live

        ↓

home.set_device(
    room="study",
    device="light",
    state="on"
)

        ↓

MQTT

        ↓

ESP32

        ↓

Relay

        ↓

💡 Light ON
```

## Why it is useful

Gemini Live can combine conversation and tool usage in the same real-time session, which reduces the need to build separate conversational STT → LLM → TTS pipelines for the cloud voice mode. citeturn293599search1turn293599search5

---

# 6. AI #4 — Gemini 3.8 Live Extended Thinking

## Purpose

This is a specialized option for cases where Lyra needs deeper reasoning during live interaction.

Google currently describes `gemini-3.8-live-extended-thinking` as a higher-reasoning audio-to-audio model for complex, multi-step voice interactions, with background reasoning and asynchronous tool calls. citeturn293599search3

## Use Case

Do **not** make this the default for every sentence.

Use it for:

- Complex planning
- Multi-step reasoning
- Difficult study questions
- Complicated tool workflows
- Long reasoning tasks

## Example

User:

> "Lyra, I have three exams next week, two projects due, and four hours each day. Make me a realistic study plan that prioritizes everything."

Router:

```text
Simple request?
NO

Complex planning?
YES

        ↓

Gemini Live Extended Thinking

        ↓

Analyze schedule
Analyze priorities
Build plan
Use tools if necessary

        ↓

Voice answer
```

This gives Lyra a way to trade some latency for better reasoning when appropriate.

---

# 7. AI #5 — Qwen3-1.7B Local Model

## Purpose

Qwen3-1.7B is the initial **offline/local language model candidate**.

The official Qwen model card provides local inference examples and describes the model as a 1.7B-parameter conversational/text-generation model under the Apache 2.0 license. It can be served through local tools such as Transformers and OpenAI-compatible servers. citeturn652774search0turn652774search1

## Why use it

Lyra should continue functioning when:

```text
Internet = OFF
```

The local model can handle simpler tasks such as:

- Basic conversation
- Simple explanations
- Writing
- Brainstorming
- Lightweight coding help
- Memory-related requests
- Local command interpretation

## Real-life example

Internet is unavailable.

User:

> "Lyra, explain what a stack is in data structures."

Router:

```text
Current information required?
NO

Web required?
NO

Simple explanation?
YES

        ↓

Qwen3 local

        ↓

Lyra speaks the explanation
```

No cloud call is needed.

## Important limitation

The old Athlon dual-core server is CPU-limited.

Therefore:

- Use a quantized build where practical
- Keep response lengths controlled
- Don't expect cloud-model-level reasoning
- Treat the local model as the offline/fallback model

---

# 8. Local vs Cloud Decision

The router decides which model should handle a request.

## Basic routing

```text
                     USER REQUEST
                           │
                           ▼
                    ┌─────────────┐
                    │ Query Router│
                    └──────┬──────┘
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
         ▼                 ▼                 ▼
      SIMPLE            CURRENT          COMPLEX
      OFFLINE            INFO            REASONING
         │                 │                 │
         ▼                 ▼                 ▼
       Qwen3          Web + Cloud     Cloud Reasoning
```

## Example 1

> "What is recursion?"

```text
Router → Local Qwen3
```

## Example 2

> "What's the latest Java version?"

```text
Router → Online search + cloud model
```

## Example 3

> "Plan my entire week around my exams and project deadlines."

```text
Router → Memory + Calendar + cloud reasoning
```

---

# 9. AI #6 — Online Search / Grounding

## Purpose

The local model has a fixed knowledge state.

It should not pretend to know information that requires current verification.

Online search is used for:

- Current news
- Latest software releases
- Current prices
- Weather
- Sports
- Recent scientific information
- Schedules
- Current product information
- Web research

## Real-life example

User:

> "What happened in today's AI news?"

```text
Router
   ↓
Needs current information
   ↓
Online search
   ↓
Sources
   ↓
Cloud model
   ↓
Summarized answer
```

## Key rule

The model should distinguish between:

```text
Known from model knowledge
        vs
Verified from current sources
```

---

# 10. AI #7 — Memory Extraction Model

## Purpose

A small model/job extracts useful long-term information from conversations.

Example:

User:

> "Remember that I prefer short explanations when I'm studying."

Memory extractor:

```json
{
  "type": "preference",
  "key": "study_response_length",
  "value": "short",
  "source": "explicit_user_request",
  "confidence": 1.0
}
```

Then the memory database stores it.

## What it should extract

- Explicit memories
- Preferences
- Stable habits
- Project information
- Study preferences
- Repeated workflows
- Important user-defined facts

## What it should not automatically store

- Every casual sentence
- Temporary emotions
- Unverified assumptions
- Sensitive information without appropriate handling
- Contradictory preferences

---

# 11. AI #8 — Conversation Summarizer

## Purpose

Summarize conversations periodically.

This supports:

- Context compression
- Daily review
- Personalization
- Memory extraction
- Lower long-context costs

## Hourly flow

```text
00:00–00:59
Conversations
      ↓
Hourly summarizer
      ↓
Hourly summary
```

Example:

```text
Hourly Summary — 10:00–11:00

Topics:
- Binary search
- Dynamic programming
- Spotify playlist

Important user preference:
- Wants Java examples

Pending task:
- Continue DP practice
```

---

# 12. AI #9 — Daily Personalization Processor

## Purpose

At the end of the day, Lyra reviews the collected summaries and identifies **stable patterns**.

```text
Hourly Summaries
      ↓
Daily Processor
      ↓
Stable Preferences
      ↓
Memory Update
      ↓
Candidate Training Examples
```

## Example

Across several conversations, Lyra observes:

```text
User repeatedly asks:
"Give me the code in Java."

User repeatedly asks:
"Explain with a simple example."

User repeatedly asks:
"Keep the answer short first."
```

The daily processor can derive:

```text
Preference:
Java examples

Preference:
Example-first explanations

Preference:
Concise default responses
```

These go into memory/personalization.

---

# 13. AI #10 — Personalization / Fine-Tuning Model

## Important distinction

The phrase **"real-time fine-tuning"** should not mean:

```text
Every conversation
    ↓
Immediately modify production model
```

That is risky.

Instead:

```text
Conversations
     ↓
Summaries
     ↓
Candidate examples
     ↓
Quality filter
     ↓
Dataset
     ↓
Training
     ↓
Evaluation
     ↓
New model version
```

## Why?

Because otherwise Lyra could learn:

- Temporary preferences
- Incorrect answers
- Contradictory instructions
- Bad habits
- Accidental information

## What should be fine-tuned?

Fine-tuning should primarily target **behavior/style**, for example:

```text
How Lyra talks
How Lyra explains
How Lyra structures responses
How Lyra follows preferred interaction patterns
```

Do not use fine-tuning as the primary storage mechanism for changing facts.

Instead:

```text
Changing fact → Memory/RAG
Behavior/style → Fine-tuning
Capabilities → Tools
Current information → Web
```

---

# 14. The Personalization Loop

Lyra's intended learning system:

```text
                    LIVE CONVERSATION
                           │
                           ▼
                    Session Storage
                           │
             ┌─────────────┴─────────────┐
             │                           │
             ▼                           ▼
        Memory Candidate             Conversation
             │                       Summary
             ▼                           │
        Memory DB                       ▼
                                Hourly Summary
                                       │
                                       ▼
                              End-of-Day Processor
                                       │
                              ┌────────┴─────────┐
                              │                  │
                              ▼                  ▼
                        Memory Update      Training Dataset
                                                 │
                                                 ▼
                                           Quality Filter
                                                 │
                                                 ▼
                                          Dataset Version
                                                 │
                                                 ▼
                                         Optional Training
                                                 │
                                                 ▼
                                            Model v2
                                                 │
                                                 ▼
                                             Evaluate
                                                 │
                                      ┌──────────┴──────────┐
                                      ▼                     ▼
                                   Deploy                Reject
```

---

# 15. AI #11 — Embedding Model

## Purpose

An embedding model converts text into vectors so Lyra can find semantically related information.

Example:

```text
Stored memory:
"I prefer concise explanations for DSA."

User:
"Keep my algorithm answers brief."

Keyword matching:
May miss the relationship.

Semantic search:
Finds the memory.
```

## Uses

- Memory retrieval
- RAG
- Document search
- Conversation search
- Study-note retrieval

## Flow

```text
Text
 ↓
Embedding model
 ↓
Vector
 ↓
Vector database
```

Then:

```text
User query
 ↓
Embedding
 ↓
Similarity search
 ↓
Relevant memories/documents
 ↓
AI
```

---

# 16. AI #12 — RAG System

RAG means **Retrieval-Augmented Generation**.

It lets Lyra answer questions using information stored outside the model itself.

## Example

Store:

```text
DSA notes
Operating Systems PDF
Machine Learning notes
Project documentation
Personal documents
```

User:

> "Explain this topic based on my OS notes."

Flow:

```text
Question
  ↓
Embedding
  ↓
Vector search
  ↓
Relevant note sections
  ↓
Cloud or local LLM
  ↓
Answer using retrieved information
```

## Why this matters

RAG means you don't need to fine-tune the model every time you add:

- A new PDF
- New notes
- A new project
- New documentation
- A new preference

---

# 17. AI #13 — Tool/Function Calling

Tool calling is the bridge between AI reasoning and real-world actions.

The model decides:

```text
What does the user want?
Which tool should be used?
What arguments should be passed?
```

The application executes the tool.

## Example

```text
User:
"Play my study playlist."

          ↓

AI

          ↓

spotify.play_playlist(
    name="study"
)

          ↓

Application executes tool
          ↓

Spotify
```

## Tools planned for Lyra

```text
spotify.*
memory.*
search.*
calendar.*
alarm.*
system.*
home.*
```

---

# 18. AI + Spotify

Spotify should not be "inside" the language model.

Instead:

```text
Language Model
      ↓
Tool Call
      ↓
Spotify API
      ↓
Music
```

## Example

```text
User:
"Play some Arijit Singh."

AI:
spotify.search("Arijit Singh")

AI:
spotify.play(result)

Spotify:
▶ Playing
```

## Supported actions

- Search
- Play
- Pause
- Resume
- Next
- Previous
- Shuffle
- Repeat
- Queue
- Current track

---

# 19. AI + Smart Home

The AI should never directly manipulate GPIO.

Correct architecture:

```text
AI
 ↓
Tool Call
 ↓
Lyra Home Service
 ↓
MQTT
 ↓
ESP32
 ↓
Relay
 ↓
Device
```

## Example

User:

> "Turn on the bedroom light."

```text
Gemini/Qwen
     ↓
home.set_device()
     ↓
MQTT
     ↓
ESP32
     ↓
GPIO
     ↓
Relay
     ↓
Light ON
```

## Why this architecture is important

It provides:

- Permission checks
- Logging
- Validation
- Device abstraction
- Easy ESP32 replacement
- Safer execution

---

# 20. AI + Computer Control

Future tool examples:

```text
system.open_application()
system.shutdown()
system.lock()
system.volume_up()
system.volume_down()
system.run_script()
```

The local/cloud model decides which tool to use, but **application code executes the actual operation**.

Sensitive operations should require explicit confirmation or authentication.

---

# 21. AI + Memory Example

### Day 1

User:

> "Remember that I prefer Java."

Memory:

```text
language_preference = Java
```

### Day 2

User:

> "Give me the solution."

Memory retrieval:

```text
Java preference
```

AI:

> Provides Java code.

No fine-tuning required.

---

# 22. AI + RAG Example

User adds a PDF:

```text
Operating Systems Notes.pdf
```

RAG pipeline:

```text
PDF
 ↓
Text extraction
 ↓
Chunking
 ↓
Embeddings
 ↓
Vector database
```

Later:

> "Explain deadlock based on my notes."

```text
Question
 ↓
Vector search
 ↓
Relevant OS note chunks
 ↓
LLM
 ↓
Answer
```

---

# 23. AI + Online Search Example

User:

> "What is the latest version of Python?"

Router:

```text
Current information?
YES

       ↓

Online search

       ↓

Current sources

       ↓

Cloud model

       ↓

Answer
```

The local model doesn't need to know the current version.

---

# 24. AI + Offline Example

Internet goes down.

User:

> "What is a binary tree?"

Router:

```text
Requires internet?
NO

       ↓

Qwen3 local

       ↓

Answer
```

Lyra continues functioning.

---

# 25. AI + Fallback Example

Local model is unable to provide a useful answer.

```text
User
 ↓
Router
 ↓
Local Qwen
 ↓
Confidence/requirement check
 ↓
Needs online reasoning
 ↓
Gemini Live / cloud model
 ↓
Answer
```

The user still experiences this as:

```text
One assistant: LYRA
```

---

# 26. Provider Independence

Lyra should never depend on one model provider.

## Example

```text
AIProvider
├── GeminiProvider
├── OpenAIProvider
├── LocalQwenProvider
└── FutureProvider
```

The core can call:

```python
response = ai.chat(request)
```

without knowing which provider is underneath.

## Benefits

- Easy model upgrades
- Provider outages are easier to handle
- Cost optimization
- Local fallback
- A/B testing
- Model evaluation
- Future-proofing

---

# 27. Recommended AI Routing Table

| Situation | Preferred AI |
|---|---|
| Wake word | Local wake-word model |
| Speech detection | Local VAD |
| Normal offline chat | Qwen3-1.7B |
| Simple offline explanation | Qwen3-1.7B |
| Real-time voice | Gemini 3.8 Live |
| Complex live reasoning | Gemini 3.8 Live Extended Thinking |
| Current information | Web/search + cloud model |
| Personal memory retrieval | Embeddings + memory DB |
| Document questions | RAG + selected LLM |
| Hourly summary | Small/fast text model |
| Daily personalization | Small/fast text model |
| Spotify command | LLM + tool calling |
| Smart-home command | LLM + tool calling + MQTT |
| Computer command | LLM + tool calling |
| Future model personalization | Local fine-tuned model |

---

# 28. Model Selection Logic

The router should consider:

```text
1. Does the request require current information?
2. Does it require an external tool?
3. Does it contain sensitive/private information?
4. Does it require complex reasoning?
5. Is the internet available?
6. Is low latency important?
7. Is the task suitable for the local model?
```

Then choose:

```text
LOCAL
ONLINE
HYBRID
TOOL
```

---

# 29. Example: One Conversation Using Multiple AI Components

Imagine:

> "Hey Lyra."

Wake-word model:

```text
Detected
```

User:

> "What is recursion?"

Router:

```text
Simple + no current information
→ Qwen3 local
```

Lyra answers.

User:

> "Now tell me the latest Java release."

Router:

```text
Current information
→ Web + Cloud AI
```

User:

> "Play my coding playlist."

Router:

```text
Music intent
→ Spotify tool
```

User:

> "Remember that I like to study Java at night."

Memory extractor:

```text
preference:
night_study_language = Java
```

One conversation.

Multiple internal components.

Still one assistant:

> **Lyra**

---

# 30. Model Training Strategy

## Base Model

Start with a strong pretrained model.

```text
Base Model
     ↓
Prompt / System Instructions
     ↓
Memory
     ↓
Tools
```

This should be enough for the first working release.

## Personalization Later

Once enough high-quality data exists:

```text
Conversation Data
      ↓
Curated Dataset
      ↓
Training
      ↓
Personalized Model
```

## Training should be optional

Lyra should continue working even if:

```text
No fine-tuned model exists
```

That is essential for maintainability.

---

# 31. RTX 4050 as the Training Machine

The stronger development machine can be used for:

- Dataset preparation
- LoRA/QLoRA experiments
- Model evaluation
- Quantization
- Local model testing
- Speech-model experimentation

The old Athlon machine can remain the always-on production server.

```text
RTX 4050 PC
     │
     ├── Train
     ├── Evaluate
     └── Quantize
              │
              ▼
        Personalized Model
              │
              ▼
      Old Athlon Server
              │
              ▼
            Lyra
```

---

# 32. What Each AI Is NOT Responsible For

| Component | Do NOT make it responsible for |
|---|---|
| Wake-word model | Answering questions |
| VAD | Understanding language |
| Local LLM | Current web facts |
| Cloud voice model | Permanent memory storage |
| Memory extractor | Making major decisions |
| Embeddings | Generating final answers |
| RAG | Performing physical device actions |
| Tool layer | Generating natural-language answers |
| Spotify API | Understanding arbitrary conversation |
| ESP32 | Running the main AI brain |

This separation keeps the system clean.

---

# 33. Overall AI Decision Flow

```mermaid
flowchart TD
    A[User says "Hey Lyra"] --> B[Wake Word Detection]
    B --> C[VAD / Listen]
    C --> D[Voice Request]

    D --> E[Lyra Core]
    E --> F[Query Router]

    F --> G{Needs Tool?}

    G -->|Spotify| H[Spotify Tool]
    G -->|Home| I[MQTT / ESP32]
    G -->|Calendar| J[Calendar Tool]
    G -->|System| K[System Tool]
    G -->|No| L{Needs Current Info?}

    L -->|Yes| M[Web Search / Online API]
    L -->|No| N{Internet Available?}

    N -->|Yes| O{Realtime Conversation?}
    N -->|No| P[Local Qwen3]

    O -->|Yes| Q[Gemini 3.8 Live]
    O -->|No| R[Cloud Text Model]

    M --> S[Answer Generation]
    P --> S
    Q --> S
    R --> S

    H --> S
    I --> S
    J --> S
    K --> S

    S --> T[Memory Retrieval]
    T --> U[Final Response]
    U --> V[Voice Output]
    V --> W[Conversation Storage]

    W --> X[Hourly Summary]
    X --> Y[Daily Personalization]
    Y --> Z[Candidate Training Dataset]
```

---

# 34. Recommended Initial AI Stack

## Production Voice

**Gemini 3.8 Live**

For the main real-time cloud voice interaction. Google currently documents it as the default low-latency Live API model. citeturn293599search1

## Offline

**Qwen3-1.7B**

For a lightweight local language-model fallback on the old server. citeturn652774search0

## Deep Voice Reasoning

**Gemini 3.8 Live Extended Thinking**

Use selectively for complicated reasoning rather than every request. citeturn293599search3

## Memory

**Embedding model + database + memory extractor**

## Current information

**Web search / grounding**

## Actions

**Function/tool calling**

## Personalization

**Memory first, optional fine-tuning later**

---

# 35. Final Mental Model

Think of Lyra like a human assistant with specialized abilities:

```text
                         LYRA
                           │
              ┌────────────┼────────────┐
              │            │            │
              ▼            ▼            ▼
            Ears         Brain         Hands
              │            │            │
          Wake/VAD       LLMs          Tools
                           │            │
                  ┌────────┼───────┐    │
                  │        │       │    │
                  ▼        ▼       ▼    ▼
                Local    Cloud    Web  Spotify
                Qwen    Gemini          Home
                                        System
                                         │
                                        ▼
                                       ESP32
```

**Ears** hear you.

**Router** decides what needs to happen.

**Local AI** keeps Lyra useful offline.

**Cloud AI** handles advanced real-time conversation.

**Web/search** supplies current information.

**Memory/RAG** gives Lyra knowledge about you and your documents.

**Tools** let Lyra perform actions.

**Personalization** gradually adapts Lyra to your preferred behavior.

From the user's perspective, all of those components are simply:

> **Lyra.**

---

# 36. Sources

- Google Gemini API Models: https://ai.google.dev/gemini-api/docs/models
- Gemini 3.8 Live: https://ai.google.dev/gemini-api/docs/models/gemini-3.8-live
- Gemini Live API: https://ai.google.dev/gemini-api/docs/live-api/get-started-sdk
- Gemini Live Capabilities: https://ai.google.dev/gemini-api/docs/live-api/capabilities
- Gemini 3.8 Live Extended Thinking: https://ai.google.dev/gemini-api/docs/models/gemini-3.8-live-extended-thinking
- Qwen3-1.7B: https://huggingface.co/Qwen/Qwen3-1.7B
- OpenAI Realtime-2 reference (alternative provider): https://developers.openai.com/api/docs/models/gpt-realtime-2

---

# 37. Initial AI Milestone

The first AI milestone is complete when:

```text
"Hey Lyra"
      ↓
Wake
      ↓
Voice conversation
      ↓
Router chooses:
    Local / Online / Tool
      ↓
Memory added/retrieved
      ↓
Lyra responds naturally
      ↓
Conversation ends
      ↓
Lyra sleeps
      ↓
Hourly summary
      ↓
Daily personalization
```

At that point, Lyra has a genuine **multi-model AI architecture** rather than being tied to one chatbot API.

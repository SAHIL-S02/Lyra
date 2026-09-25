# Lyra — Initial Feature Specification

> **Project:** Lyra  
> **Type:** Personal AI Voice Assistant  
> **Initial Goal:** Build a modular, cross-platform, voice-first personal assistant that works offline whenever possible, uses online services when required, can control Spotify, and gradually personalizes itself to the user.

---

## 1. Product Vision

Lyra is a personal AI assistant designed to provide:

- Natural real-time voice conversation
- Offline-first AI capabilities
- Online web/search fallback for information that requires current knowledge
- Personal memory and personalization
- Spotify/music control
- Automatic conversation session management
- Future smart-home control through ESP32 devices
- A modular architecture that can run on both Windows and Linux
- Easy replacement/upgrading of the underlying AI provider or model

### Core principle

Lyra should separate four major concerns:

```text
AI Model
    = intelligence / reasoning

Memory
    = what Lyra knows about the user

Tools
    = what Lyra can do

Personalization
    = how Lyra behaves for the user
```

This separation should remain part of the architecture from the first version.

---

# 2. Initial Feature Set

## 2.1 Real-Time Voice Chat

The primary interface of Lyra will be voice.

### Wake Word

Lyra should remain in a low-power/sleep state until the user calls its name.

Example:

> "Hey Lyra"

or:

> "Lyra"

Expected flow:

```text
Sleeping
   ↓
Wake word detected
   ↓
Listening
   ↓
User speaks
   ↓
AI processes request
   ↓
Lyra responds with voice
   ↓
Continue conversation OR return to sleep
```

### Requirements

- Configurable wake word
- Local wake-word detection where practical
- No unnecessary cloud request while sleeping
- Clear indication when Lyra is listening
- Clear indication when Lyra is responding
- Ability to manually put Lyra to sleep
- Ability to wake Lyra again without restarting the application

### Manual commands

Examples:

- `"Lyra, go to sleep"`
- `"Stop listening"`
- `"Cancel"`
- `"Wake up, Lyra"`

---

## 2.2 Natural Multi-Turn Conversation

Lyra should support a continuous conversation rather than treating every sentence as a completely new request.

Example:

> User: "Explain binary search."

> Lyra: "Binary search works by repeatedly dividing..."

> User: "Give me an example."

Lyra should understand that "an example" refers to binary search.

### Requirements

- Conversation sessions
- Context retention within a session
- Follow-up questions
- Context-aware pronouns and references
- Configurable conversation history
- Session timeout
- Manual session reset

---

## 2.3 Automatic Sleep / Conversation End

Lyra should automatically return to its sleeping state after the conversation ends.

Possible triggers:

- Configurable silence timeout
- User says goodbye
- User explicitly says "sleep"
- Session reaches a configured idle threshold

Example:

```text
User: "Thanks Lyra."
Lyra: "You're welcome."
        ↓
Short idle period
        ↓
Lyra enters sleep mode
```

### Important behavior

Lyra should **not** continuously stream microphone audio to the AI service while it is sleeping.

---

# 3. Real-Time Audio

## 3.1 Audio Input

The system should support:

- USB microphone
- Laptop microphone
- Future ESP32 microphone nodes
- Streaming PCM audio
- Configurable sample rate and audio format

For a dedicated hardware version, an I2S microphone such as an INMP441-class microphone can be used with ESP32-S3 hardware.

## 3.2 Audio Output

Lyra should support:

- Laptop speakers
- USB speakers
- Bluetooth speakers where supported
- Future ESP32-connected speakers
- Streaming audio output
- Volume control

## 3.3 Voice Activity Detection

Lyra should detect:

- When the user starts speaking
- When the user stops speaking
- Long silence
- Background noise

This allows automatic turn detection without requiring a physical button.

## 3.4 Barge-In / Interruption

The user must be able to interrupt Lyra while it is speaking.

Example:

```text
Lyra: "The main idea behind machine learning is—"

User: "Stop. Explain neural networks instead."

Lyra:
    stop current audio
    cancel/adjust current response
    listen to new request
```

This is a major feature for making Lyra feel like a real voice assistant.

---

# 4. Offline-First AI

Lyra should be capable of working without an internet connection for tasks that do not require online information.

## 4.1 Local AI

Use a small local/quantized model for tasks such as:

- Casual conversation
- Basic explanations
- Writing assistance
- Brainstorming
- Simple coding questions
- General reasoning
- Personal memory retrieval
- Local command interpretation

### Hardware target

The initial server can run on the existing old laptop:

- AMD Athlon dual-core CPU
- 16 GB RAM

Because the CPU is limited, the local model should be kept relatively small and optimized/quantized.

Large local LLMs should not be a requirement for the initial version.

---

# 5. Online AI / Web Fallback

When the local AI cannot reliably answer a question, or when the request requires current information, Lyra should be able to use online services.

## 5.1 When Lyra should use the internet

Examples:

- Latest news
- Today's weather
- Current prices
- Current sports scores
- Latest software documentation
- Recent events
- Current schedules
- Current product information
- Web research
- Information newer than the local model's knowledge
- Requests containing terms such as:
  - latest
  - current
  - today
  - recently
  - this week
  - live

## 5.2 Intelligent Routing

Lyra should not simply trust the local model's confidence.

Instead, use a router:

```text
User Question
     ↓
Query Router
     ↓
 ┌──────────────┬──────────────┬───────────────┐
 │              │              │
Local          Online         Both
Only           Required       Required
 │              │              │
 ▼              ▼              ▼
Local LLM    Web/API        Local + Web
```

## 5.3 Online Answer Quality

When online information is used:

- Search current sources
- Prefer authoritative sources
- Include source information where appropriate
- Distinguish verified information from model-generated reasoning
- Avoid pretending a local model knows current events
- Cache only information that is safe and useful to cache

---

# 6. AI Provider Abstraction

Lyra should not be permanently tied to one AI provider.

The architecture should support interchangeable providers such as:

- Gemini
- OpenAI
- Other compatible cloud AI providers
- Local models

Example interface:

```python
response = ai.chat(request)
```

instead of allowing the rest of the application to depend directly on a specific provider's API.

### Goal

The following should be replaceable without rebuilding Lyra:

- LLM provider
- Voice model
- STT provider
- TTS provider
- Search provider
- Local model

This makes future upgrades significantly easier.

---

# 7. Personalization

Lyra should become personalized to the user over time.

## 7.1 Personality

Configurable characteristics:

- Name: **Lyra**
- Creator identity/name
- Response style
- Formality
- Verbosity
- Preferred language
- Greeting style
- Preferred voice
- Custom system rules

Example identity:

```text
You are Lyra, a personal AI assistant created by the user.
```

## 7.2 User Preferences

Lyra can remember explicitly provided preferences such as:

- Preferred explanation style
- Preferred response length
- Study preferences
- Common routines
- Frequently used commands
- Favorite music/playlists
- Device names
- Preferred units
- Language preferences

Example:

> "Remember that I prefer short explanations when studying."

Lyra stores this as a memory rather than requiring model retraining.

---

# 8. Long-Term Memory

Lyra should have a persistent memory layer.

## 8.1 Memory Types

### Personal Facts

Information the user explicitly asks Lyra to remember.

### Preferences

How the user likes things done.

### Habits

Repeated patterns observed with appropriate safeguards.

### Project Context

Important information about ongoing projects.

### Study Context

Subjects, goals, topics being studied, etc.

### Conversation Summaries

Compact summaries of relevant previous conversations.

---

## 8.2 Explicit Memory Commands

Support commands such as:

- "Remember this..."
- "Save this..."
- "Forget that."
- "What do you remember about me?"
- "Delete my memory."
- "Don't remember this conversation."

This gives the user direct control over stored information.

---

# 9. Continuous Personalization / "Real-Time Fine Tune"

The planned feature called **Real-Time Fine Tune** should initially be implemented as a **Continuous Personalization Pipeline**.

The purpose is to make Lyra learn from conversations without retraining the production model every hour.

## 9.1 Hourly Conversation Summary

Every hour:

```text
Recent Conversations
       ↓
Summarization
       ↓
Important events/preferences/facts
       ↓
Hourly Summary
```

The summary can contain:

- Topics discussed
- Important decisions
- User preferences mentioned
- Tasks created
- Unresolved questions
- Useful personal context
- Important project information

## 9.2 End-of-Day Processing

At the end of the day:

```text
Hourly Summaries
       +
Selected Conversations
       ↓
Daily Personalization Job
       ↓
Extract stable preferences
       ↓
Update memory
       ↓
Generate candidate training examples
       ↓
Validate / evaluate
       ↓
Store new dataset version
```

## 9.3 Training Dataset Generation

The system can generate structured training examples such as:

```json
{
  "instruction": "User prefers concise study explanations.",
  "response_style": "Short, direct, example-oriented."
}
```

Or conversational examples:

```json
{
  "user": "Explain this topic quickly.",
  "assistant": "Give a concise explanation first, followed by one example."
}
```

## 9.4 Important Rule

Do **not** automatically fine-tune the production model on every day's raw conversations.

Use:

```text
Conversation
    ↓
Summary
    ↓
Memory
    ↓
Candidate training data
    ↓
Quality filter
    ↓
Evaluation
    ↓
Optional fine-tuning
```

Reasons:

- Avoid contradictory examples
- Avoid learning temporary preferences
- Avoid low-quality conversations
- Avoid poisoning the model with incorrect information
- Prevent unnecessary training cost
- Keep model versions stable
- Make changes reversible

---

# 10. Model Versioning

Every personalization/training iteration should be versioned.

Example:

```text
Lyra Model
 ├── base
 ├── personalized-v1
 ├── personalized-v2
 └── personalized-v3
```

Store:

- Version ID
- Creation date
- Dataset version
- Training configuration
- Evaluation results
- Changelog

Allow rollback:

```text
personalized-v3
     ↓ problem detected
rollback
     ↓
personalized-v2
```

---

# 11. Spotify Integration

Spotify should be implemented as a tool/service rather than embedded into the AI model.

## 11.1 Core Music Commands

Lyra should support:

- Play a song
- Play an artist
- Play an album
- Play a playlist
- Pause
- Resume
- Next track
- Previous track
- Shuffle
- Repeat
- Volume control
- Current track
- Search Spotify
- Queue music

Examples:

> "Lyra, play Arijit Singh."

> "Lyra, play my study playlist."

> "Lyra, skip this song."

> "Lyra, what song is playing?"

## 11.2 Music Modes

Potential presets:

- Study
- Relax
- Workout
- Sleep
- Focus

Example:

> "Lyra, start study mode."

Possible behavior:

```text
Study mode
    ↓
Start study playlist
    ↓
Set appropriate volume
    ↓
Start Pomodoro (future)
```

---

# 12. Tool / Function Calling

Lyra should use tools for actions rather than asking the language model to directly manipulate systems.

Example:

```text
User:
"Play my study playlist."

AI
 ↓
spotify.play_playlist("study")

Tool
 ↓
Spotify
```

Other future tools:

```text
spotify.*
alarm.*
calendar.*
home.*
system.*
search.*
memory.*
```

This keeps actions predictable and testable.

---

# 13. Future ESP32 Smart Home Integration

This is not required for the first voice-only prototype, but the initial architecture must be ready for it.

## 13.1 ESP32 Role

ESP32 devices will act as:

- Relay controllers
- Sensors
- Voice terminals
- Local IoT nodes
- Device status reporters

## 13.2 Communication

Recommended protocol:

**MQTT**

Example topics:

```text
home/bedroom/light/set
home/bedroom/light/state

home/study/fan/set
home/study/fan/state

home/kitchen/light/set
home/kitchen/light/state
```

## 13.3 Future Flow

```text
User:
"Lyra, turn on my bedroom light."

        ↓

Lyra AI
        ↓
home.set_device(
    room="bedroom",
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

Light ON
```

---

# 14. Security for Future Smart Home

Any action that can affect physical safety or access should require stronger authorization.

Examples:

- Door unlocking
- Alarm disarming
- Security mode changes
- Gate control
- Sensitive system commands

Do not rely only on voice recognition.

Possible authorization layers:

```text
Voice command
     ↓
Identity/session check
     ↓
PIN / phone confirmation / biometric
     ↓
Action
```

---

# 15. Cross-Platform Requirement

Lyra must run on:

- Windows
- Linux

The goal is to avoid OS-specific logic in the core application.

## 15.1 Platform Adapter

Example:

```text
platform/
├── base.py
├── windows.py
└── linux.py
```

The core can call:

```python
system.shutdown()
system.volume_up()
system.open_application()
```

The platform adapter handles the OS-specific implementation.

---

# 16. Recommended Technology Direction

### Core language

**Python**

Good for:

- AI integration
- FastAPI
- WebSockets
- automation
- databases
- machine learning
- audio processing

### Backend

**FastAPI**

For:

- REST API
- WebSocket connections
- authentication
- tool execution
- device management

### Database

Start with:

**SQLite**

Later:

**PostgreSQL**

Potential stored data:

- Users
- Memories
- Conversations
- Summaries
- Preferences
- Tasks
- Music preferences
- Device registry
- Model versions

### Real-Time Communication

**WebSockets**

Useful for:

- Live audio
- Streaming AI responses
- ESP32 communication gateways
- Real-time events

### Smart Home

**MQTT**

### Deployment

Prefer:

**Docker / Docker Compose**

This makes Windows/Linux deployment much easier.

---

# 17. Configuration Management

All secrets and environment-specific settings should be externalized.

Example:

```text
.env
```

Possible settings:

```text
AI_PROVIDER=
AI_API_KEY=
SPOTIFY_CLIENT_ID=
SPOTIFY_CLIENT_SECRET=
DATABASE_URL=
MQTT_BROKER=
WAKE_WORD=
LOG_LEVEL=
```

Never hard-code API keys into source code.

---

# 18. Logging and Diagnostics

Lyra should have structured logs from the beginning.

Track:

- Assistant startup/shutdown
- Wake-word detection
- Voice session start/end
- API errors
- AI response latency
- Search latency
- Spotify errors
- Tool calls
- Memory updates
- Scheduler jobs
- Model changes

Example:

```text
[19:30:03] Wake word detected
[19:30:04] Voice session started
[19:30:05] AI request sent
[19:30:07] AI response received
[19:30:07] TTS started
[19:30:10] Session ended
[19:30:20] Lyra sleeping
```

---

# 19. Health Monitoring

Create a simple health endpoint:

```text
GET /health
```

Example:

```json
{
  "lyra": "online",
  "ai": "connected",
  "spotify": "connected",
  "memory": "healthy",
  "voice": "ready"
}
```

This will simplify debugging.

---

# 20. Local Web Dashboard

A small web dashboard is recommended even for the initial version.

Possible sections:

### Overview

```text
Lyra
Status: Online
AI: Connected
Spotify: Connected
Voice: Ready
```

### Conversation History

- Recent sessions
- Search conversations
- Delete conversation
- Export conversation

### Memory

- View memories
- Add memory
- Edit memory
- Delete memory
- Clear all memory

### Personalization

- Current personality configuration
- Preferences
- Dataset versions
- Personalization history

### System

- CPU usage
- RAM usage
- API latency
- Service status
- Logs

### Settings

- AI provider
- Voice
- Wake word
- Language
- Response style
- Sleep timeout

---

# 21. Privacy

Because Lyra is a voice assistant, privacy should be part of the initial design.

Requirements:

- Local wake-word detection where possible
- Do not upload audio while sleeping
- Store only required audio
- Allow conversation deletion
- Allow memory deletion
- Allow disabling persistent memory
- Keep API keys server-side
- Encrypt remote connections
- Keep sensitive device commands authenticated
- Give the user control over what is remembered

---

# 22. Initial User Experience

A typical interaction should look like:

```text
Lyra sleeping...

User:
"Hey Lyra."

Lyra:
"Yes?"

User:
"What's the current weather?"

        ↓

Router detects current information is required

        ↓

Online search / API

        ↓

Lyra:
"It is currently ..."

User:
"Okay. Play my study playlist."

        ↓

Spotify tool

        ↓

Music starts

User:
"Thanks."

        ↓

Lyra:
"You're welcome."

        ↓
Idle timeout

        ↓

Lyra sleeping...
```

---

# 23. Initial Command Categories

The first version should recognize at least these categories:

```text
CONVERSATION
    General questions
    Follow-up questions
    Explanations

SYSTEM
    Sleep
    Wake
    Stop
    Cancel

MUSIC
    Play
    Pause
    Resume
    Next
    Previous
    Search

MEMORY
    Remember
    Forget
    View memory

WEB
    Search
    Current information

PERSONALIZATION
    Change response style
    Change voice
    Change preferences
```

---

# 24. Suggested Small Features for v0.1

These are relatively small but significantly improve usability.

## "Stop"

Immediately stop speaking.

## "Repeat"

Repeat the previous response.

## "Short answer"

Temporarily reduce response length.

## "Explain more"

Continue with a deeper explanation.

## Session reset

> "New conversation."

This clears short-term conversational context without deleting long-term memory.

## Sleep timer

Automatically put Lyra to sleep after a configurable period.

## Status command

> "Lyra, status."

Possible response:

> "AI is connected, Spotify is connected, memory is available, and I'm ready."

## Debug mode

A developer-only mode showing:

- Chosen AI provider
- Router decision
- Tools called
- Response latency
- Errors

---

# 25. Recommended Initial Scope

The first working release should focus on:

### Must Have

- Wake word
- Voice input
- Real-time AI conversation
- Voice output
- Multi-turn conversation
- Barge-in
- Automatic sleep
- Offline local AI
- Online fallback/search
- Basic memory
- Explicit remember/forget commands
- Spotify integration
- Provider abstraction
- Windows support
- Linux support
- Configuration management
- Logging
- Basic web dashboard

### Should Have

- Hourly conversation summaries
- Daily summaries
- Preference extraction
- Personalization dataset generation
- Model versioning
- Rollback support
- Health endpoint
- Export/delete data

### Later

- Actual fine-tuning
- ESP32 smart-home control
- MQTT device network
- Alarms/reminders
- Calendar
- Computer control
- Vision
- Security/access control
- Proactive assistant
- Multi-room voice nodes

---

# 26. Recommended Development Order

```text
Phase 1
│
├── Lyra Core
├── Voice input/output
├── Wake word
├── AI provider
└── Basic conversation

        ↓

Phase 2
│
├── Real-time streaming
├── VAD
├── Barge-in
└── Automatic sleep

        ↓

Phase 3
│
├── Local AI
├── Online router
├── Web search
└── Provider abstraction

        ↓

Phase 4
│
├── Memory
├── Hourly summaries
├── Daily summaries
└── Personalization

        ↓

Phase 5
│
├── Spotify
├── Tools
└── Music controls

        ↓

Phase 6
│
├── Dashboard
├── Logging
├── Health monitoring
└── Windows/Linux packaging

        ↓

Phase 7
│
├── ESP32
├── MQTT
├── Smart home
└── Sensors/relays
```

---

# 27. Long-Term Vision

Once the initial system is stable, Lyra can evolve into:

```text
                         LYRA
                           │
          ┌────────────────┼────────────────┐
          │                │                │
       AI Brain         Memory           Tools
          │                │                │
      Local + Cloud     RAG/DB       Spotify/Home/Web
          │                │                │
          └────────────────┼────────────────┘
                           │
                    Personal Agent
                           │
          ┌────────────────┼────────────────┐
          ▼                ▼                ▼
       Computer          Study           Smart Home
          │                │                │
          ▼                ▼                ▼
       Windows/Linux     Learning       ESP32/MQTT
```

The final goal is not simply an Alexa clone. Lyra should become a **portable, modular personal AI platform** whose AI model, memory system, tools, voice layer, and hardware can all be upgraded independently.

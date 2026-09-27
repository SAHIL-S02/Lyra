import asyncio
from app.memory.manager import MemoryManager
from dotenv import load_dotenv
from google import genai
from google.genai import types
from app.memory.tools import (
    MEMORY_FUNCTIONS,
    MEMORY_TOOL_DECLARATIONS,
)
from .base import AIProvider
from app.memory.manager import MemoryManager

load_dotenv()


class GeminiLiveProvider(AIProvider):
    """Real-time Gemini Live provider for Lyra."""

    MODEL = "gemini-3.8-live"

    def __init__(self) -> None:
        self.client = genai.Client()
        self.memory = MemoryManager()

    async def respond(self, text: str) -> str:
        """
        Text-based test through Gemini Live.

        Gemini Live returns AUDIO, while output transcription
        allows us to inspect the response as text.
        """

        if not text.strip():
            raise ValueError("Input text cannot be empty.")

        config = types.LiveConnectConfig(
            response_modalities=["AUDIO"],
            output_audio_transcription=types.AudioTranscriptionConfig(),
        )

        async with self.client.aio.live.connect(
            model=self.MODEL,
            config=config,
        ) as session:

            await session.send_realtime_input(text=text)

            response_text: list[str] = []

            async for response in session.receive():
                if not response.server_content:
                    continue

                transcription = (
                    response.server_content.output_transcription
                )

                if transcription and transcription.text:
                    response_text.append(transcription.text)

                if response.server_content.turn_complete:
                    break

            result = "".join(response_text).strip()

            if not result:
                raise RuntimeError(
                    "Gemini Live returned no output transcription."
                )

            return result

    async def run_voice_session(
        self,
        audio_queue,
        playback,
        stop_event: asyncio.Event | None = None,
    ) -> None:
        """
        Run a persistent real-time voice conversation.

        stop_event:
            Used by the voice controller to terminate the session
            and return Lyra to wake-word mode.
        """

        if stop_event is None:
            stop_event = asyncio.Event()
        identity = self.memory.get_lyra_identity()

        creator = identity.get(
            "creator",
            "not configured",
        )

        version = identity.get(
            "system_version",
            "not configured",
        )
        config = types.LiveConnectConfig(
            response_modalities=["AUDIO"],

            input_audio_transcription=types.AudioTranscriptionConfig(),
            output_audio_transcription=types.AudioTranscriptionConfig(),

            system_instruction=f"""
You are Lyra, a personal AI assistant.

========================
CORE LYRA IDENTITY
========================

Your name: Lyra
Your creator: {creator}
Your application version: {version}

These values come from Lyra's persistent SQLite memory.

When the user asks:

"Who created you?"
→ Answer using the stored creator: {creator}

"Who is your creator?"
→ Answer using the stored creator: {creator}

"What is your version?"
→ Answer using the stored application version: {version}

"What's your current version?"
→ Answer using the stored application version: {version}

Do NOT replace Lyra's creator with the underlying AI provider,
model provider, Google, or any other provider identity.

========================
LONG-TERM MEMORY
========================

Lyra has persistent long-term memory.

Available memory tools:

- remember_memory
- search_memory
- update_memory
- forget_memory

IMPORTANT MEMORY RULES:

1. Only save information when the user explicitly asks you to
   remember, save, keep, or not forget it.

2. When answering a question that depends on previously stored
   user information, use search_memory.

3. When the user changes an existing memory:
   - First identify the existing memory.
   - Use its exact existing key.
   - Use update_memory.
   - Do NOT create a new key for the same fact.

4. Never create key variants such as:
   - creator_name
   - my_creator
   - creator_full_name
   - assistant_creator
   when the existing canonical key is:
   - creator

5. Similarly, use:
   system_version
   for Lyra's application version.

6. remember_memory may create a new memory when no existing
   logical memory exists.

7. update_memory is for changing an existing memory and must use
   the exact existing key.

8. forget_memory should only be used when the user explicitly
   asks to forget/remove/delete information.

9. Never save ordinary casual conversation.

10. After a successful save/update/delete operation, acknowledge
    the action naturally.

========================
MEMORY UPDATE EXAMPLE
========================

Existing memory:

creator = "S.K. Sahil Uddin"

User:
"Don't use dots between S and K. Save it."

Correct process:

search_memory("creator")

then:

update_memory(
    key="creator",
    value="SK Sahil Uddin",
    category="fact"
)

Do NOT create:

creator_name

Do NOT create:

my_creator

Do NOT create:

creator_full_name
""",

            tools=[
                {
                    "function_declarations": MEMORY_TOOL_DECLARATIONS
                }
            ],

            realtime_input_config=types.RealtimeInputConfig(
                automatic_activity_detection=types.AutomaticActivityDetection(
                    disabled=False,
                    prefix_padding_ms=40,
                    silence_duration_ms=500,
                )
            ),
        )

        async with self.client.aio.live.connect(
            model=self.MODEL,
            config=config,
        ) as session:

            async def send_audio() -> None:
                """Send microphone audio to Gemini Live."""

                while True:
                    event_type, data = await audio_queue.get()

                    if event_type == "AUDIO":

                        if not data:
                            continue

                        await session.send_realtime_input(
                            audio=types.Blob(
                                data=data,
                                mime_type="audio/pcm;rate=16000",
                            )
                        )

                    elif event_type == "END_OF_TURN":

                        print(
                            "\nSending audio stream end...",
                            flush=True,
                        )

                        await session.send_realtime_input(
                            audio_stream_end=True
                        )

                    elif event_type == "STOP":
                        return

            async def receive_audio() -> None:
                """Receive Gemini Live responses continuously."""

                while True:

                    async for response in session.receive():

                        # ---------------------------------------------
                        # FUNCTION / MEMORY TOOL CALLS
                        # ---------------------------------------------

                        if response.tool_call:

                            function_responses = []

                            for function_call in response.tool_call.function_calls:

                                name = function_call.name
                                args = dict(function_call.args or {})

                                print(
                                    f"\n🔧 Tool call: {name}({args})",
                                    flush=True,
                                )

                                function = MEMORY_FUNCTIONS.get(name)

                                if function is None:

                                    result = {
                                        "success": False,
                                        "error": f"Unknown tool: {name}",
                                    }

                                else:

                                    try:
                                        result = function(**args)

                                    except Exception as exc:

                                        result = {
                                            "success": False,
                                            "error": (
                                                f"{type(exc).__name__}: {exc}"
                                            ),
                                        }

                                function_responses.append(
                                    types.FunctionResponse(
                                        name=name,
                                        id=function_call.id,
                                        response=result,
                                    )
                                )

                            await session.send_tool_response(
                                function_responses=function_responses
                            )

                            continue

                        # ---------------------------------------------
                        # NORMAL SERVER CONTENT
                        # ---------------------------------------------

                        if not response.server_content:
                            continue

                        server_content = response.server_content

                        # ---------------------------------------------
                        # BARGE-IN / INTERRUPTION
                        # ---------------------------------------------

                        if server_content.interrupted:

                            print(
                                "\n\n⚡ Lyra interrupted — "
                                "clearing audio buffer...\n",
                                flush=True,
                            )

                            playback.clear()

                            continue

                        # ---------------------------------------------
                        # USER TRANSCRIPTION
                        # ---------------------------------------------

                        input_transcription = (
                            server_content.input_transcription
                        )

                        if (
                            input_transcription
                            and input_transcription.text
                        ):

                            print(
                                f"\nYou: {input_transcription.text}",
                                end="",
                                flush=True,
                            )

                        # ---------------------------------------------
                        # LYRA TRANSCRIPTION
                        # ---------------------------------------------

                        output_transcription = (
                            server_content.output_transcription
                        )

                        if (
                            output_transcription
                            and output_transcription.text
                        ):

                            print(
                                f"\nLyra: {output_transcription.text}",
                                end="",
                                flush=True,
                            )

                        # ---------------------------------------------
                        # LYRA AUDIO
                        # ---------------------------------------------

                        model_turn = server_content.model_turn

                        if model_turn:

                            for part in model_turn.parts:

                                if not part.inline_data:
                                    continue

                                audio_data = part.inline_data.data

                                if audio_data:
                                    playback.add(audio_data)

                        # ---------------------------------------------
                        # TURN COMPLETE
                        # ---------------------------------------------

                        if server_content.turn_complete:

                            print(
                                "\n",
                                flush=True,
                            )
            async def wait_for_stop() -> None:
                """Wait until the controller requests shutdown."""

                await stop_event.wait()

                print(
                    "\nStopping Gemini Live session...",
                    flush=True,
                )

                await audio_queue.put(("STOP", b""))

            send_task = asyncio.create_task(
                send_audio()
            )

            receive_task = asyncio.create_task(
                receive_audio()
            )

            stop_task = asyncio.create_task(
                wait_for_stop()
            )

            try:
                done, pending = await asyncio.wait(
                    {
                        send_task,
                        receive_task,
                        stop_task,
                    },
                    return_when=asyncio.FIRST_COMPLETED,
                )

                # If the controller requested stop,
                # the STOP event will terminate send_audio().
                if stop_task in done:
                    if not send_task.done():
                        await send_task

                # Any unexpected task completion means
                # the session should terminate as well.
                else:
                    stop_event.set()

            except asyncio.CancelledError:
                stop_event.set()

                send_task.cancel()
                receive_task.cancel()
                stop_task.cancel()

                await asyncio.gather(
                    send_task,
                    receive_task,
                    stop_task,
                    return_exceptions=True,
                )

                raise

            finally:
                stop_event.set()

                for task in (
                    send_task,
                    receive_task,
                    stop_task,
                ):
                    if not task.done():
                        task.cancel()

                await asyncio.gather(
                    send_task,
                    receive_task,
                    stop_task,
                    return_exceptions=True,
                )
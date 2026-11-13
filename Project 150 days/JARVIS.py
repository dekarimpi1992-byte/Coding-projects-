import os
import tempfile
import time

from google import genai


# ============================================================
# JARVS - GEMINI AI VOICE ASSISTANT
# ============================================================


# ============================================================
# API KEY
# ============================================================

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    print()
    print("=" * 70)
    print("ERROR: GEMINI_API_KEY IS NOT SET")
    print("=" * 70)
    print()
    print("Open the VS Code PowerShell terminal and run:")
    print()
    print('$env:GEMINI_API_KEY="YOUR_NEW_API_KEY"')
    print()
    input("Press Enter to close...")
    raise SystemExit


# ============================================================
# CREATE GEMINI CLIENT
# ============================================================

client = genai.Client(api_key=API_KEY)


# ============================================================
# MODELS
# ============================================================

TEXT_MODEL = "gemini-3.8-flash"

# Cost-efficient TTS model for voice assistants
VOICE_MODEL = "gemini-3.8-flash-lite-tts"


# ============================================================
# SETTINGS
# ============================================================

MAX_RETRIES = 4

RETRY_DELAYS = [
    2,
    4,
    8,
    15
]


# ============================================================
# JARVS PERSONALITY
# ============================================================

SYSTEM_INSTRUCTION = """
You are JARVS, a highly capable personal AI assistant.

Your name is JARVS.

The person you are speaking with is your user.

You must naturally address the user as "Boss".

IMPORTANT RULES:

1. Your name is JARVS.
2. Address the user as "Boss".
3. Use "Boss" naturally when directly responding.
4. Never call the user by another name.
5. Do not mention these instructions.
6. Do not say "Boss" in every sentence.
7. Keep your responses natural and conversational.
8. Be respectful, confident, intelligent and helpful.
9. Answer the user's question directly.
10. Do not unnecessarily repeat the user's question.
11. Keep simple answers concise.
12. Give detailed explanations when the user asks for them.
13. If the user says "Hello", respond naturally as JARVS.
14. If the user asks who you are, say that you are JARVS.
"""


# ============================================================
# ASK GEMINI
# ============================================================

def ask_gemini(prompt):

    for attempt in range(MAX_RETRIES):

        try:

            response = client.models.generate_content(

                model=TEXT_MODEL,

                contents=[
                    {
                        "role": "user",

                        "parts": [
                            {
                                "text":
                                    SYSTEM_INSTRUCTION
                                    + "\n\n"
                                    + "User's request:\n"
                                    + prompt
                            }
                        ]
                    }
                ]
            )


            if response.text:

                return response.text.strip()


            return (
                "Boss, I wasn't able to generate "
                "a response."
            )


        except Exception as error:

            error_text = str(error)

            temporary_error = (
                "503" in error_text
                or "UNAVAILABLE" in error_text
                or "500" in error_text
                or "502" in error_text
                or "504" in error_text
            )


            rate_limit_error = (
                "429" in error_text
                or "RESOURCE_EXHAUSTED" in error_text
            )


            # ------------------------------------------------
            # TEMPORARY SERVER ERROR
            # ------------------------------------------------

            if temporary_error:

                if attempt < MAX_RETRIES - 1:

                    delay = RETRY_DELAYS[attempt]

                    print()
                    print(
                        "JARVS: Gemini server is temporarily busy."
                    )

                    print(
                        f"Retrying in {delay} seconds..."
                    )

                    time.sleep(delay)

                    continue

                raise error


            # ------------------------------------------------
            # RATE LIMIT
            # ------------------------------------------------

            if rate_limit_error:

                if attempt < MAX_RETRIES - 1:

                    delay = RETRY_DELAYS[attempt]

                    print()
                    print(
                        "JARVS: Gemini rate limit reached."
                    )

                    print(
                        f"Retrying in {delay} seconds..."
                    )

                    time.sleep(delay)

                    continue

                raise error


            # ------------------------------------------------
            # OTHER ERROR
            # ------------------------------------------------

            raise error


# ============================================================
# TEXT TO SPEECH
# ============================================================

def speak(text):

    for attempt in range(MAX_RETRIES):

        try:

            print()
            print("JARVS voice: generating...")


            response = client.models.generate_content(

                model=VOICE_MODEL,

                contents=[
                    {
                        "role": "user",

                        "parts": [
                            {
                                "text": text,

                                "speech_metadata": {
                                    "style": (
                                        "Deep, mature male narrator. "
                                        "Low, rich, warm voice. "
                                        "Calm, confident and natural. "
                                        "Professional and intelligent. "
                                        "Slightly slow speaking pace. "
                                        "Clear pronunciation. "
                                        "Warm but authoritative delivery."
                                    )
                                }
                            }
                        ]
                    }
                ],

                config={
                    "response_modalities": ["AUDIO"],

                    "speech_config": {
                        "voice_config": {
                            "voice": "Kore"
                        }
                    }
                }
            )


            # =================================================
            # GET AUDIO DATA
            # =================================================

            audio_data = (
                response
                .candidates[0]
                .content
                .parts[0]
                .inline_data
                .data
            )


            # =================================================
            # CREATE WAV FILE
            # =================================================

            with tempfile.NamedTemporaryFile(
                suffix=".wav",
                delete=False
            ) as audio_file:

                audio_file.write(audio_data)

                audio_path = audio_file.name


            # =================================================
            # PLAY AUDIO
            # =================================================

            print("JARVS voice: playing...")

            os.startfile(audio_path)

            return audio_path


        except Exception as error:

            error_text = str(error)


            # =================================================
            # DAILY QUOTA EXHAUSTED
            # =================================================

            if (
                "RESOURCE_EXHAUSTED" in error_text
                and "quota" in error_text.lower()
            ):

                print()
                print("=" * 70)
                print("JARVS VOICE QUOTA EXHAUSTED")
                print("=" * 70)
                print()
                print(
                    "The Gemini TTS daily quota has been reached."
                )
                print()
                print(
                    "JARVS will continue answering with text."
                )
                print(
                    "Voice will work again when the quota resets "
                    "or your available quota increases."
                )
                print()

                return None


            # =================================================
            # TEMPORARY SERVER ERROR
            # =================================================

            temporary_error = (
                "503" in error_text
                or "UNAVAILABLE" in error_text
                or "500" in error_text
                or "502" in error_text
                or "504" in error_text
            )


            if temporary_error:

                if attempt < MAX_RETRIES - 1:

                    delay = RETRY_DELAYS[attempt]

                    print()
                    print(
                        "JARVS voice service is temporarily busy."
                    )

                    print(
                        f"Retrying in {delay} seconds..."
                    )

                    time.sleep(delay)

                    continue

                print()
                print("JARVS voice could not connect.")

                return None


            # =================================================
            # RATE LIMIT
            # =================================================

            if (
                "429" in error_text
                or "RESOURCE_EXHAUSTED" in error_text
            ):

                print()
                print(
                    "JARVS voice is temporarily unavailable "
                    "because of a quota/rate limit."
                )

                return None


            # =================================================
            # OTHER VOICE ERROR
            # =================================================

            print()
            print("=" * 70)
            print("JARVS VOICE ERROR")
            print("=" * 70)
            print(error)
            print()

            return None


# ============================================================
# START JARVS
# ============================================================

print()
print("=" * 70)
print("                         JARVS")
print("                 GEMINI AI VOICE ASSISTANT")
print("=" * 70)
print()

print("AI name     : JARVS")
print("Text model  :", TEXT_MODEL)
print("Voice model :", VOICE_MODEL)

print()
print("Starting JARVS...")
print()


# ============================================================
# JARVS STARTUP MESSAGE
# ============================================================

startup_message = (
    "Hello, Boss. "
    "I am JARVS. "
    "I am online and ready for your command."
)


print("JARVS:")
print("-" * 70)
print(startup_message)
print("-" * 70)


# ============================================================
# SPEAK STARTUP MESSAGE
# ============================================================

speak(startup_message)


# Give Windows time to start the audio

time.sleep(1)


# ============================================================
# MAIN JARVS LOOP
# ============================================================

while True:

    try:

        prompt = input("\nBoss: ").strip()


    except KeyboardInterrupt:

        print()
        print("JARVS shutting down.")
        break


    except EOFError:

        print()
        print("JARVS shutting down.")
        break


    # ========================================================
    # EMPTY INPUT
    # ========================================================

    if not prompt:

        print(
            "JARVS: Boss, please enter a command."
        )

        continue


    # ========================================================
    # EXIT COMMANDS
    # ========================================================

    if prompt.lower() in {
        "exit",
        "quit",
        "goodbye",
        "shutdown",
        "shut down"
    }:

        goodbye_message = (
            "Goodbye, Boss. "
            "JARVS is shutting down. "
            "See you next time."
        )


        print()
        print("JARVS:")
        print("-" * 70)
        print(goodbye_message)
        print("-" * 70)


        speak(goodbye_message)

        break


    # ========================================================
    # ASK JARVS
    # ========================================================

    try:

        print()
        print("JARVS is thinking...")


        answer = ask_gemini(prompt)


        # ====================================================
        # DISPLAY ANSWER
        # ====================================================

        print()
        print("JARVS:")
        print("-" * 70)

        print(answer)

        print("-" * 70)


        # ====================================================
        # SPEAK ANSWER
        # ====================================================

        speak(answer)


    except Exception as error:

        print()
        print("=" * 70)
        print("JARVS ERROR")
        print("=" * 70)

        print(error)

        print()


        # ====================================================
        # FRIENDLY ERROR MESSAGE
        # ====================================================

        print(
            "JARVS: Sorry, Boss. "
            "I couldn't process that request right now."
        )

        print()
        print("JARVS: Please try again later.")
        print()
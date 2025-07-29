# co-author : Gemini 2.5 Pro Preview
import logging

import pyttsx3

# Set up a logger for this module.
# In a larger application, the root logger would typically be configured elsewhere.
# For a standalone script or a module intended to be used as a utility,
# getting a logger instance like this is standard.
logger = logging.getLogger(__name__)


def text_to_speech_pyttsx3(text, voice_id=None, rate=150, volume=1.0):
    """
    Synthesizes text to speech using pyttsx3.

    Args:
        text (str): The text to synthesize.
        voice_id (str, optional): The ID of the voice to use. If None, uses the default voice.
                                  Defaults to None.
        rate (int, optional): The speech rate (words per minute). Defaults to 150.
        volume (float, optional): The speech volume (0.0 to 1.0). Defaults to 1.0.
    """
    try:
        logger.info("Initializing pyttsx3 engine.")
        engine = pyttsx3.init()

        # Configure speech rate
        logger.debug(f"Setting speech rate to: {rate}")
        engine.setProperty("rate", rate)

        # Configure volume
        logger.debug(f"Setting volume to: {volume}")
        engine.setProperty("volume", volume)

        # Get available voices
        voices = engine.getProperty("voices")
        logger.debug(f"Found {len(voices)} voices available on the system.")

        # To list available voices and their properties in detail, uncomment the following:
        # for voice in voices:
        #     logger.debug(f"Voice Details - ID: {voice.id} | Name: {voice.name} | Lang: {voice.languages} | Gender: {voice.gender}")

        # Select a specific voice
        if voice_id:
            logger.info(f"Attempting to set voice ID to: {voice_id}")
            engine.setProperty("voice", voice_id)
            # Verify if voice was set (optional, pyttsx3 doesn't always provide easy verification)
            # current_voice = engine.getProperty('voice')
            # logger.debug(f"Current voice ID set to: {current_voice}")
            # if current_voice != voice_id:
            #     logger.warning(f"Failed to set voice ID to {voice_id}. Current voice is {current_voice}")
        else:
            logger.info("No specific voice_id provided, using default voice.")
            # Example to select a specific voice type if no voice_id is given
            # This part is illustrative and would need adaptation based on available voices on your system.
            # for voice in voices:
            #     if "english" in voice.name.lower() and voice.gender == "female": # Adapt condition
            #         engine.setProperty('voice', voice.id)
            #         logger.info(f"Selected voice programmatically: {voice.name} ({voice.id})")
            #         break

        logger.info(f"Synthesizing text: '{text}'")
        engine.say(text)
        engine.runAndWait()  # Blocks until all spoken text has been heard

        # engine.stop() # Usually not needed after runAndWait() for simple use cases.
        # Consider if managing event loop manually or for specific platform issues.

        logger.info("Speech synthesis complete.")

    except Exception as e:
        logger.error(f"An error occurred during pyttsx3 operation: {e}", exc_info=True)
        # exc_info=True will include traceback information in the log for errors.


if __name__ == "__main__":
    # Basic logging configuration for when the script is run directly.
    # This will print log messages of level INFO and above to the console.
    logging.basicConfig(
        level=logging.INFO,  # Change to logging.DEBUG for more detailed output
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    logger.info("--- Text-to-Speech Example Script Starting ---")

    # Example: Listing available voices (more detailed logging if DEBUG is enabled)
    logger.info("Attempting to list available voices (details will show if log level is DEBUG)...")
    try:
        temp_engine = pyttsx3.init()
        available_voices = temp_engine.getProperty("voices")
        if not available_voices:
            logger.warning("No voices found by pyttsx3 engine.")
        for i, v in enumerate(available_voices):
            log_message = f"Voice {i + 1}: ID='{v.id}', Name='{v.name}', Langs={v.languages}, Gender='{v.gender}'"
            if logger.isEnabledFor(logging.DEBUG):  # Log detailed voice info only if DEBUG is on
                logger.debug(log_message)
            elif i < 5:  # Log first few voices at INFO level for a quick glance
                logger.info(f"Voice {i + 1} (sample): Name='{v.name}', ID='{v.id}'")
        if len(available_voices) > 5 and not logger.isEnabledFor(logging.DEBUG):
            logger.info(f"... and {len(available_voices) - 5} more voices (set log level to DEBUG to see all).")
        temp_engine.stop()  # Clean up the temporary engine
    except Exception as e:
        logger.error(f"Could not list voices: {e}", exc_info=True)

    logger.info("--- Default voice example ---")
    text_to_speech_pyttsx3("Hello, this is a test using the default voice settings.")

    logger.info("--- Custom settings example (faster and louder) ---")
    text_to_speech_pyttsx3("This is a faster and louder message.", rate=220, volume=0.95)

    # Example for finding and using a specific voice ID
    # Replace with an actual voice ID from your system after listing them.
    # macos_daniel_voice_id = 'com.apple.speech.synthesis.voice.daniel' # Example for macOS
    # windows_zira_voice_id = 'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_ZIRA_11.0' # Example for Windows

    # selected_voice_id = None # Set this to a valid ID from your system
    # if selected_voice_id:
    #     logger.info(f"--- Attempting to use specific voice ID: {selected_voice_id} ---")
    #     text_to_speech_pyttsx3("This should be a specifically selected voice.", voice_id=selected_voice_id)
    # else:
    #     logger.info("--- Specific voice ID example skipped (no voice_id set) ---")

    logger.info("--- French example (will use default if no French voice is specifically set/found) ---")
    text_to_speech_pyttsx3("Bonjour le monde.")

    logger.info("--- Text-to-Speech Example Script Finished ---")

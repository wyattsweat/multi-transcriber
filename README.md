# multi-transcriber

Run speech_to_text_gui.py (GUI) and loop.py (handles the communication and basic transcription) in different terminals and click Start on the GUI to begin the transcription.

You will need either a VOSK library or replace vosk_result['text'] with r.recognize_google(audio, show_all=True) for it to translate anything.

The VOSK libraries can be found https://alphacephei.com/vosk/models

Also check requirements.txt for the import requirements.

import os
import pyaudio
import json
from pathlib import Path
from pydub import AudioSegment

path="wavs\\"

p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16,
                     channels=1,
                     rate=16000,
                     input=True,
                     frames_per_buffer=8000)
                     
stream.start_stream()

thread_ctr=0
ctr=0
SAMPLE_RATE = 16000
print("Listening...")
audio_stream=None
while True:
    data = stream.read(4000, exception_on_overflow = False)
    if (audio_stream != None):
        audio_stream+=data
    else:
        audio_stream=data
    #print(".")
    
    ctr+=1
    
    if(ctr>10):
        print("Running")
        audio=AudioSegment(audio_stream, sample_width=2, frame_rate=16000, channels=1)
        export_file=path + str(thread_ctr)+".wav"
        audio.export(export_file, format="wav")
        audio_stream=None
        thread_ctr+=1
        if(thread_ctr>9):
            thread_ctr=0
        ctr=0
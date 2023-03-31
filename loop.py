import json
from pathlib import Path
import speech_recognition as sr

import numpy as np
from pydub import AudioSegment
from vosk import KaldiRecognizer, Model, SetLogLevel

from pydiar.models import BinaryKeyDiarizationModel
from pydiar.util.misc import optimize_segments

import time
from datetime import datetime


import pandas as pd

df = pd.read_csv('known.csv')
print(df.head())

for i in range(0,len(df)):
    SAMPLE_RATE = 16000
    pre_audio = AudioSegment.from_wav(df['file'][i])
    pre_audio = pre_audio.set_frame_rate(SAMPLE_RATE)
    pre_audio = pre_audio.set_channels(1)

    try: 
        pre+=pre_audio
    except: 
        pre=pre_audio    
        

def speaker_name(ctr,speaker):
    global df
    if(ctr<len(df)):
        df.loc[ctr, 'speaker_id'] = speaker
        
def get_speaker_name(ctr,speaker):
    speaker_name=df['name'].loc[df['speaker_id'] == speaker].head(1)
    if(len(speaker_name)<1):
        ser = {'a': 'unknown'}
        unknown = pd.Series(data=ser, index=['a'])
        return unknown
    else:
        return speaker_name

def format_time(time):
    secs = time % 60
    mins = time // 60
    hours = int(mins // 60)
    mins = int(mins % 60)
    return f"{hours:02d}:{mins:02d}:{secs:.3f}"



r = sr.Recognizer()
mic = sr.Microphone(device_index=0)

def callback(recognizer, audio):
    global df
    print("Call")
    wave=audio.get_wav_data()
    with open("mic.wav", "wb") as f:
        f.write(wave)
    wav_file = 'mic.wav'

    #from pydiar's examples/generate_webvtt.py with slight modifications
    
    SAMPLE_RATE = 16000
    SAMPLE_RATE = 16000
    #pre_audio = AudioSegment.from_wav("pre.wav")
    #pre_audio = AudioSegment.from_wav("voices.wav")
    #audio = AudioSegment.from_wav("mic.wav")
    #pre_audio = pre_audio.set_frame_rate(SAMPLE_RATE)
    #pre_audio = pre_audio.set_channels(1)
    
    #audio = AudioSegment.from_wav("wyatt_line.wav")
    #audio = AudioSegment.from_wav("test.wav")
    #audio = AudioSegment.from_wav("voices.wav")
    #audio = AudioSegment.from_wav("sunday_line.wav")
    current_audio = AudioSegment.from_wav("mic.wav")
    current_audio = current_audio.set_frame_rate(SAMPLE_RATE)
    current_audio = current_audio.set_channels(1)

    audio=pre+current_audio
    
    try:
        f = open("settings.txt", "r")
        with open("settings.txt", "r+") as settings:
            et=settings.read()
        r.energy_threshold=int(et)
        df = pd.read_csv('known.csv')
        print(df.head())
        diarization_model = BinaryKeyDiarizationModel()        
        segments = diarization_model.diarize(
            SAMPLE_RATE, np.array(audio.get_array_of_samples())
        )
        
        segments = optimize_segments(segments)

        print("segments: " + str(len(segments)))

        SetLogLevel(-1)
        model = Model("vosk-model\\")

        ctr=0
        for segment in segments:
            rec = KaldiRecognizer(model, SAMPLE_RATE)
            rec.SetWords(False)
            st = format_time(segment.start)
            end = format_time(segment.start + segment.length)
            print(f"{st} --> {end}")
            data_start = int(segment.start * 1000)
            data_end = int((segment.start + segment.length) * 1000)
            speaker_name(ctr,segment.speaker_id)
            print(segment.start)
            print(pre.duration_seconds-1)
            if(segment.start>pre.duration_seconds-1):
                if (len(segments) > 1):
                    data = audio[data_start:data_end]
                else:
                    data = audio
                rec.AcceptWaveform(data.get_array_of_samples().tobytes())
                vosk_result = json.loads(rec.FinalResult())
                print(str(get_speaker_name(ctr,segment.speaker_id).to_string(index=False)) + ": " + str(vosk_result['text']) + "\n")
                now = datetime.now()
                print(now)
                current_time = now.strftime("%H:%M:%S")
                counter=time.time()
                counter2=str(now.strftime("%H%M%S")) + str(ctr)
                if (len(str(vosk_result['text']))>0):
                    f = open("convo.csv", "a")
                    #f.write(str(segment.speaker_id)+","+str(vosk_result['text']) + "," + str(counter) + "," + str(current_time)+ "\n")
                    name=str(get_speaker_name(ctr,segment.speaker_id).to_string(index=False))
                    if(str(name) in "unknown"):
                        f.write("speaker" + str(segment.speaker_id) +","+str(vosk_result['text']) + "," + str(counter) + "," + str(current_time)+ "\n")
                    else:
                        f.write(str(get_speaker_name(ctr,segment.speaker_id).to_string(index=False))+","+str(vosk_result['text']) + "," + str(counter) + "," + str(current_time)+ "\n")
                    f.close()
                    fn="temp\\" + str(counter2) + ".wav"
                    data.export(out_f = fn, format = "wav")

                #print(f"<{speaker_name(ctr,segment.speaker_id).to_string(index=False)}>{vosk_result['text']}\n")
            ctr+=1
    except:
        try:
            print("Too short")
            txt=r.recognize_google(audio, show_all=True)
            print(txt)
        except:
            e=1

with mic as source:
    #r.adjust_for_ambient_noise(source)
    print("Start Speaking")
    #audio=r.listen(source)
    

stop_listening = r.listen_in_background(mic, callback,5)

while 1==1:
    #print("Listening")
    time.sleep(0.5)


stop_listening()
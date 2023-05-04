import os
import json
from pathlib import Path
import numpy as np
from pydub import AudioSegment
from pydub.playback import play
from scipy import spatial
import wave
from time import sleep
from vosk import KaldiRecognizer, Model, SetLogLevel, SpkModel
import time
from datetime import datetime
import io
import pandas as pd
import whisper

whisp = whisper.load_model("medium.en")

lang = "en-US"
DEBUG = True

SetLogLevel(-1)

df = pd.read_csv('voiceprints.csv')
df['dist']=3




def cosine_dist(x, y):
    nx = np.array(x)
    ny = np.array(y)
    return 1 - np.dot(nx, ny) / np.linalg.norm(nx) / np.linalg.norm(ny)


class Vosk:
    def __init__(self):
        spk_model = SpkModel("vosk-model-spk/")
        
        
        model = Model("vosk-model/")
        self.rec = KaldiRecognizer(model, 16000)
        self.rec.SetSpkModel(spk_model)
        
        self.rec2 = KaldiRecognizer(model, 16000)
        self.rec2.SetSpkModel(spk_model)


    def run(self):
        global df
        SAMPLE_RATE = 16000
        print("Listening...")
        audio_stream=None
        ctr=0
        while True:
            path = "wavs\\"
            directory = os.listdir(path)
            sleep(0.01)
            if(len(directory)>0):
                print(directory[0])
                filename=path+str(directory[0])
                data = wave.open(filename, "rb")
                audio_stream = data.readframes(40000)
                
                self.rec2.AcceptWaveform(audio_stream)
                res2 = json.loads(self.rec2.FinalResult())

                if "spk" in res2:
                    print("--------------------")
                    for dfi in range(len(df)):
                        arr=np.fromstring(str(df['voiceprint'][dfi][1:-1]), dtype='float', sep=",")
                        df['dist'].iloc[dfi]=cosine_dist(arr, res2["spk"])

                print(df[['user','dist']].sort_values(by=['dist']).head(7))
                
                
                result = whisp.transcribe(filename)
                
                print(result["text"])
                print(str(df.sort_values(by=['dist']).iloc[0][0]), ":" + str(result["text"]))
                
                now = datetime.now()
                current_time = now.strftime("%H:%M:%S")
                counter=time.time()
                counter2=str(now.strftime("%H%M%S")) + str(ctr)

                if(len(res2["text"])>0):
                    f = open("convo.csv", "a")
                    tex=str(result["text"]).replace(',','')
                    try:
                        vp=str(res2["spk"]).replace('[', '"')
                        vp=vp.replace(']', '"')
                        
                        if(float(df[['dist']].sort_values(by=['dist']).iloc[0]) < 2.85):
                            try:
                                change = pd.read_csv('changes.csv')
                                print(change.head())
                                replacement=change[change['name']==str(df.sort_values(by=['dist']).iloc[0][0])]
                                for i in range(len(replacement)):
                                    tex=tex.replace(replacement["wrong"].iloc[i],replacement["right"].iloc[i])
                                print("Updated text: " + str(tex))
                            except:
                                e=1
                        
                            f.write(str(df.sort_values(by=['dist']).iloc[0][0])+","+str(tex) + "," + str(counter) + "," + str(current_time)+ "," + str(vp) + "\n")
                        else:
                            f.write(str("unknown")+","+str(txt) + "," + str(counter) + "," + str(current_time) + "," + str(vp) + "\n")
                    except:
                        try:
                            tex=str(result["text"]).replace(',','')
                            f.write(str("unknown")+","+str(txt) + "," + str(counter) + "," + str(current_time)+ "," + str("") + "\n")
                        except:
                            e=1
                    f.close()
                    ctr+=1
                    if ctr>2:
                        ctr=0
                        df = pd.read_csv('voiceprints.csv')
                        df['dist']=3
                data.close()
                audio_stream=None
                os.remove(path+str(directory[0]))
                


if __name__ == '__main__':
    stt = Vosk()
    print(stt.run())

import os
from time import sleep
from tkinter import *
from tkinter import font
import threading
from socket import *
from select import *
from queue import Queue
import sys
import pandas as pd
import time
import gtts
from playsound import playsound
import re
import numpy as np
import difflib

master = Tk() #create the GUI window

pre_slider_value=1

#put the test program in a seperate thread so it doesn't lock up the GUI
def test_program_thread():
    q = Queue() # Shared queue for sending dialog info to the GUI
    edits = Queue() # Shared queue for sending edited text in the GUI back to the backend (isn't used right now)
    thread1 = threading.Thread(target=test_program, args=(q,edits)) # Thread receives piped input and prints it on the screen
    thread2 = threading.Thread(target=read_input, args=(q,edits)) # Thread where backend would be run, theoretically. Feeds dummy text into the queue
    thread1.start()
    thread2.start()

# Dummy function emulating how text would be fed into the GUI
def read_input(q, edits):
    global pre_slider_value
    counter=time.time()
    counter2=time.time()
    #buff = [("Barry", "[12:01:43]: I think we should reconsider."), ("Bart", "[12:01:56]: That's your opinion."), ("Barry", "[12:02:04]: This is ridiculous!"), ("Bart", "[12:02:15]: I'm sorry.")] # This shouldn't be in the final
    while True:
        df = pd.read_csv('convo.csv')
        buff=[]
        for i in range(0,len(df)):
            #if(float(df['ctr'][i])>counter):
            if(float(df['ctr'][i])>counter2):
                #text2 = "{" + str(df['time'][i]) + "]: " + str(df['text'][i] + str(df['ctr'][i]))
                # text2 = "{" + str(df['time'][i]) + "]: " + str(df['text'][i])
                # buff.append([str(df['speaker_id'][i]),text2])
                text2 = str(df['speaker_id'][i]) + "[" + str(df['time'][i]) + "]: " + str(df['text'][i])
                buff.append(text2)
                q.put(buff.pop(0))
        counter=time.time()
        counter2=float(df['ctr'][i])
        if len(buff) > 0:
            q.put(buff.pop(0))
        sleep(0.01) # just to make it look like a real conversation
        if(noise_slider.get() != pre_slider_value):
            noise_slider.get()
            with open("settings.txt", "w") as setf:
                setf.write(str(noise_slider.get()))
                setf.close()

# Displays text fed in from the shared Queue
def test_program(q, edits):
    k = 0 # The index of the current line of text to be printed next
    buff = [] # Holds the text to be printed
    selected_index = "" # Index of the selected text for editing
    which_selected = -1 # 0 if the selected text is dialog, 1 if selected text is a name
    while True:
        if not q.empty(): # get one item from shared queue if the queue is not empty
            buff.append(q.get())
            print(buff)
        if k < len(buff): # display text from buffer as long as there is text in buff left to print
            listbox_text.insert(END, buff[k])
            # listbox_speaker.insert(END, buff[k][0])
            # listbox_text.yview(END)
            # listbox_speaker.yview(END)
            k += 1
        # These two variables store the index of selected text for editing
        selected_text = listbox_text.curselection()
        # selected_speaker = listbox_speaker.curselection()
        if not len(selected_text) == 0: # checking if a line of dialog has been selected
            edit_text = listbox_text.get(selected_text) # get string of text at index
            name_text = edit_text.split("[")
            # Display dialog text in a text box that the user can edit and then submit changes
            if text_edit_box.compare("end-1c", "==", "1.0") and name_edit_box.compare("end-1c", "==", "1.0"): # checking if edit box is initially empty (nothing was selected for editing)
                which_selected = 0
                selected_index = selected_text
                name_edit_box.insert('end', name_text[0])
                text_edit_box.insert('end', name_text[1])
            #elif not selected_text == selected_index or not which_selected == 0: # edit box already has something in it, but we want to change it to the currently selected text
            elif not selected_text == selected_index:
                name_edit_box.delete("1.0", 'end')
                text_edit_box.delete("1.0", 'end')
                selected_index = selected_text
                which_selected = 0
                name_edit_box.insert('end', name_text[0])
                text_edit_box.insert('end', name_text[1])
        else:
            listbox_text.yview(END)
        # elif not len(selected_speaker) == 0: # checking if a name has been selected
        #     edit_text = listbox_speaker.get(selected_speaker)
        #     if text_box.compare("end-1c", "==", "1.0"):
        #         which_selected = 1
        #         selected_index = selected_speaker
        #         text_box.insert('end', edit_text)
        #     elif not selected_speaker == selected_index or not which_selected == 1:
        #         which_selected = 1
        #         text_box.delete("1.0", 'end')
        #         selected_index = selected_speaker
        #         text_box.insert('end', edit_text)
        master.update() #I don't think this line is necessary, but put it here just in case
    print(k)

# Function for the button that submits the changes to a line of text or name. Updates the UI to reflect the change
def text_editor():
        selected = listbox_text.curselection()
        # checking to see whether a name or a line of dialog was edited
        if not len(selected) == 0: # a line of dialog was edited
            text = text_edit_box.get("1.0", "end-1c")
            name = name_edit_box.get("1.0", "end-1c")
            selected_text = listbox_text.get(selected)
            edited_line = name + "[" + text
            
            try:
                df = pd.read_csv('convo.csv')
                ti=re.search(r"(\[)(.*?)(\])", edited_line)
                print(ti[2])
                temp_df=df.loc[df['time']==ti[2]]
                vp=temp_df['spk'].iloc[0]

                
                f = open("voiceprints.csv", "a")
                f.write(str(name)+',"'+ str(vp) + '"\n')
                f.close()
            except:
                ti=0
            
            
            if not edited_line == selected_text:
                listbox_text.delete(selected)
                listbox_text.insert(selected, edited_line)
                listbox_text.selection_clear(0, 'end')
                name_edit_box.delete("1.0", 'end')
                text_edit_box.delete("1.0", 'end')
                print("We changed some text!")
                try:
                    diffl = difflib.Differ()
                    change=pd.read_csv('changes.csv')

                    diff = diffl.compare(str(selected_text).split(), str(edited_line).split())

                    x=''.join(diff)
                    print(x)
                    
                    result=re.search("- (\w+)\- (\w+)\+ (\w+)\+ (\w+)", x)
                    try:
                        change.loc[len(change.index)] = [str(name), result.group(1), result.group(3)]
                        change.loc[len(change.index)] = [str(name), result.group(2), result.group(4)]
                    except:
                        i=1
                        
                    result=re.search(r"- (\w+)\+ (\w+)", x)
                    
                    try:
                        change.loc[len(change.index)] = [str(name), result.group(1), result.group(2)]
                    except:
                        i=1
                    change.to_csv('changes.csv', index=False)
                except:
                    ti=0
                
                
        # else:
        #     selected = listbox_speaker.curselection()
        #     if not len(selected) == 0: # a name was edited
        #         text = text_box.get("1.0", "end-1c")
        #         selected_text = listbox_speaker.get(selected)
        #         if not text == selected_text:
        #             listbox_speaker.delete(selected)
        #             listbox_speaker.insert(selected, text)
        
def deselect():
    listbox_text.selection_clear(0, 'end')
    name_edit_box.delete("1.0", 'end')
    text_edit_box.delete("1.0", 'end')

# Change the font size based on the selection in the dropdown menu
def font_size():
    # listbox_speaker['font'] = font.Font(size=clicked.get())
    listbox_text['font'] = font.Font(size=clicked.get())

# Save the text to be spoken by the text-to-speech function
def text_to_speech():
    tts_saved_text = tts_box.get("1.0", "end-1c")
    tts_box.delete("1.0", "end-1c")
    tts = gtts.gTTS(tts_saved_text)
    tts.save("temptts.mp3")
    print(tts_saved_text)
    audio_file = os.path.dirname(__file__) + "temptts.mp3"
    playsound(audio_file)
    


def scroll(*args):
    # listbox_speaker.yview(*args)
    listbox_text.yview(*args)

def mouse_wheel(event):
    # listbox_speaker.yview("scroll", event.delta, "units")
    listbox_text.yview("scroll", event.delta, "units")


# set the gui window dimensions and the title on the GUI
master.minsize(width=1500, height=900)
master.wm_title("Stack Problem")

# Start button is set to y and starts the test program when hit
start_button = Button(master, text='START', command=test_program_thread)
start_button.place(x=5, y=5)

# Font size options for the dropdown menu (default is 10)
options = [10, 12, 14, 16, 18]
clicked = IntVar()
clicked.set(10)

# dropdown menu for font size
size_dropdown = OptionMenu(master, clicked, *options)
size_dropdown.pack()

# scroll bar for the terminal outputs
#scrollbar = Scrollbar(master)
#scrollbar.place(x=1200, y=220)

# Dialog box. Auto scrolls to the bottom but also has the scroll bar incase you want to go back up
listbox_text = Listbox(master, width=125, height=13, font=font.Font(size=clicked.get())) #yscrollcommand=scrollbar.set)
listbox_text.place(x=5, y=200)
listbox_text.see(END)
#scrollbar.config(command=scroll) # Just realized the scrollbar only works on the dialog. It doesn't work on the names yet. The name box and the dialog box need to scroll in tandem

# Speaker box
# listbox_speaker = Listbox(master, width=10, height=13, font=font.Font(size=clicked.get()), yscrollcommand=scrollbar.set)
# listbox_speaker.place(x=5, y=300)
# listbox_speaker.see(END)

# change mouse wheel keybinding to scroll both lists
listbox_text.bind("<MouseWheel>", mouse_wheel)
# listbox_speaker.bind("<MouseWheel>", mouse_wheel)

# button for confirming the font size change
font_button = Button(master, text='CHANGE SIZE', command=font_size)
font_button.pack()

# Text box for editing selected text
name_edit_box = Text(master, width=10, height=2, font=("Helvetica", 18))
name_edit_box.place(x=5, y=100)
name_edit_box.config(state='normal')

text_edit_box = Text(master, width=50, height=2, font=("Helvetica", 18))
text_edit_box.place(x=150, y=100)
text_edit_box.config(state='normal')

# button for confirming a text edit
edit_button = Button(master, text='EDIT', command=text_editor)
edit_button.place(x=830, y=120)

# button for deselecting text
deselect_button = Button(master, text='DESELECT', command=deselect)
deselect_button.place(x=900, y=120)

noise_label = Label(master, text="Noise Reduction")
#noise_label.place(x=1005, y=90)

noise_slider = Scale(master, from_=0, to=100, orient=HORIZONTAL) #acquire slider value with noise_slider.get()
#noise_slider.place(x=1000, y=120)

#GUI loops here
master.mainloop()
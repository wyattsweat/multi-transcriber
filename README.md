# multi-transcriber

Whisper (the AI that transcribes speech to text) requires ffmpeg to be used.  This can be install on a Linux platform with a command like:
sudo apt-get install ffmpeg

Whisper also can make use of the GPU which is what we demoed with.

We used a CUDA (NVidia's GPU) capable Windows 10 machine and installed pytorch with a command like so:
pip3 install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu118

The above command would vary for your version of CUDA, graphics card, machine, and OS.  It can work without this but it will be much slower (about 1/10th the speed).

You can learn more about CUDA here:
https://docs.nvidia.com/cuda/cuda-installation-guide-microsoft-windows/
https://docs.nvidia.com/cuda/cuda-installation-guide-linux/
https://developer.download.nvidia.com/compute/cuda/10.1/Prod/docs/sidebar/CUDA_Installation_Guide_Mac.pdf

For the Diarization you'll need two other downloads found at https://alphacephei.com/vosk/models:
https://alphacephei.com/vosk/models/vosk-model-spk-0.4.zip
unzipped to vosk-model-spk
and
https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
unzipped to vosk-model

To install the other requirements please run pip3 install -r requirements.txt


The directory structure should look like the following at the end:

base directory
->vosk-model
->->am
->->conf
->->graph
->->ivector
->->README

->vosk-model-spk
->->final.ext.raw
->->mean.vec
->->mfcc.conf
->->README.txt
->->transform.mat

->wavs

->changes.csv
->convo.csv
->loop_v4.py
->requirements.txt
->settings.txt
->speech_to_text_gui.py
->voiceprints.csv
->writer.py


Once everything is installed, run writer.py, loop_v4.py, and speech_to_text_gui.py in parallel (separate terminals/cmd lines/etc).  loop_v4.py will generally take a minute or two to initialize and will download the Whisper AI model the first time running it which can take some time.

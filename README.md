# KokoroTTS
My GUI interface for offline Windows-based Text-To-Speech: Kokoro The Beast!!

Kokoro studio pro and the bat file and the vbs are one project. They work without a browser using a tkinter gui, just install python and you are good to go. I haven't tested with the gpu detection, coz i have none, but if you do, it will detect it automatically(🤞fingers crossed)

The kokoro web server versions are two separate trial runs i was doing: 

Your layout should look something like this: 

<img width="684" height="168" alt="image" src="https://github.com/user-attachments/assets/ad1e7668-f847-421f-b4f3-91cecae3409f" />

venv is optional for the web server versions. 

kokoro_working_cpu_webserver.py calls CPU directly from the browser and uses fastapi.

kokoro_webgpu_001.py tried calling my old radeon r5 but it constantly crashed after a consistent 100% usage meaning windows has to disable that thing, coz my screen needs some gpu too. So, if you have amd radeon r5 430 or such gpus, don't do the following or you will waste your time:

**1. Try to modify the models or patching them with several methods from online forums, it most likely fails or produces screeching sounds.

2. Try to use the gpu for computation and audio generation coz the gpu is so old, its hardware is LIMITED, it works, it loads, but it can't help you generate. Rather buy another gpu, maybe an rx 580? an nvidia one that has better newer specs? Don't dare buy gpus that are pre-2017 specifically radeon, for such work.

3. Switching operating systems isn't going to make it do anything, your hardware is limited, even if the code/web servers are perfectly capable of calling the gpu.**
 
NB: I might have hardcoded paths from my own computer, so, tweak the code a bit to fit your system.

If you have ever desired to abandon Balabolka on windows, then here's a tool I built. 

Made with Python-Tkinter, simple user interface where you paste your text, and you generate the audio.

Things to remember:

<img width="1182" height="892" alt="image" src="https://github.com/user-attachments/assets/5f7ed5cb-7eae-4122-95ad-8c32ccf4ef0d" />

Kokoro requires AI models downloaded on your computer: voices-v1.0.bin AND kokoro-v1.0.onnx

<img width="1073" height="785" alt="image" src="https://github.com/user-attachments/assets/67c2122c-4a95-4354-8957-62004e18a1a5" />

These AI models are tiny and are from huggingface.

Install espeak-ng for speech synthesis. You can also try running the tool before you install espeak-ng. It used to work for me, either way, I recommend installing it.

https://github.com/espeak-ng/espeak-ng/releases/tag/1.52.0

Install python 3.12

Create a folder, start a virtual environment (venv) with python.

Then click the .vbs to start the GUI if you want a silent start.

The .bat file is for those who want to see logs. 

Done! Enjoy generating your audio. 

If anything breaks, I'll fix it, but it might take a while. 

**GUI EXPLAINED A BIT:**

I made it to generate parts, coz I usually read a lot of books, so, while it is generating part 1, part 2 is in the queue.

You add part, it gives your audio a good name eg 001.voicename.date.mp3 so that everything is generated in order. 

If you have a beefy GPU, the tool can detect it, else you can tweak some of the code to make the GUI see the GPU. You might need to install some runtimes/dependencies for CUDA or ROCM for blazing fast/instant audio generation.

You can clean the text, load text files, listen to the audio, load entire text files and so many other features you will meet. 

The tool will be improved as we go!🚀


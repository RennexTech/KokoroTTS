# KokoroTTS
My GUI interface for offline Windows-based Text-To-Speech: Kokoro The Beast!!

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

If you have a beefy GPU I think the tool can detect it and use it, else you can tweak some of the code to make the GUI see the GPU. You might need to install some runtimes/dependencies for CUDA or ROCM for blazing fast/instant audio generation.

You can clean the text, load text files, listen to the audio, load entire text files and so many other features you will meet. 

The tool will be improved as we go!🚀


import subprocess
audio = "bengali.mp4"
command = f"cmd /c ffmpeg -i D:\\UofT_Offline\\subtitle!\\data\\{audio} -ab 160k -ac 2 -ar 44100 -vn D:\\UofT_Offline\\subtitle!\\audio\\{audio}.wav"

subprocess.call(command, shell=True)
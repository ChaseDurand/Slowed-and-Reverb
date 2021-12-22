# 【 ｓｌｏｗｅｄ　ａｎｄ　ｒｅｖｅｒｂ】
>_"Creating uninspired edits has never been easier!"_

Slowed and Reverb is a utility for easily creating aesthetic audio+visual edits.

For the audio, the input track is slowed+pitched and then convoluted with an impulse response. For the video, a random image from [/media/background](/media/background) is combined with CRT/VHS-esque grain layers, chromatic aberration, and ripple effects.

## Requirements
* Python 3.5+
* ffmpeg
* sox


## Usage
Pass an audio file as an argument. MP3 and MP4 files will export to same location as input file.
```
git clone git@github.com:ChaseDurand/Slowed-and-Reverb.git
cd Slowed-and-Reverb
python3 SlowedAndReverb.py /path/to/audio.mp3
```


## Examples
<img src="/.github/sample3.png" alt="sample3" width="500"/>
<img src="/.github/sample1.png" alt="sample1" width="500"/>
<img src="/.github/sample2.png" alt="sample2" width="500"/>

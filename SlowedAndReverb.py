import subprocess
import sys
import pathlib
import tempfile
import shutil
import random
from distutils.dir_util import copy_tree
import sox


def effects(input, tmpDirectory):
    # Apply resampling and convolution reverb to audio file
    # Because this uses filter and filter_complex, effects need to be done in 2 separate ffmpeg processes
    # Append output file with tag.
    pathInput = pathlib.Path(input)
    inputName = pathInput.stem
    extention = pathInput.suffix
    tmpName = " Slowed"
    tag = " [ s l o w e d   a n d   R e v e r b ]"
    inputSampleRate = sox.file_info.sample_rate(input)
    inputSampleRateCommand = str(round(inputSampleRate))
    print(inputSampleRateCommand)
    speed = 0.73
    resampleRate = round(inputSampleRate * speed)
    sampleRateCommand = "asetrate=" + str(resampleRate)
    intermediateAudio = pathlib.Path(tmpDirectory,
                                     inputName + tmpName + extention)
    finalAudio = pathlib.Path(tmpDirectory, inputName + tag + extention)
    subprocess.run([
        "ffmpeg", "-i", input, "-filter:a", sampleRateCommand, "-ar",
        inputSampleRateCommand, intermediateAudio
    ])  # Slow audio and resample to original sample rate
    subprocess.run([
        "ffmpeg", "-i", intermediateAudio, "-i", "media/impulse.wav",
        "-filter_complex",
        "[0] [1] afir=dry=10:wet=10 [reverb]; [0] [reverb] amix=inputs=2:weights=10 7",
        finalAudio
    ])  # Apply convolution reverb
    #Delete intermediate files
    intermediateAudio.unlink()
    return finalAudio


def createVideo(audio, tmpDirectory):
    # Create a video file using audio track and images
    # Get a random background image from background folder
    backgroundImage = random.choice(
        list(pathlib.Path("media/background/").rglob('*jpg')))
    backgroundImageCrop = pathlib.Path(tmpDirectory,
                                       "backgroundImageBlur" + ".jpg")
    grain1 = "media/grain/grain1 - CRT TV Static Noise Loop #1 [CC BY 4.0] In-Camera.mp4"
    grain2 = "media/grain/grain2 - VHS Rewind Grain Overlay Effect - freestockfootagearchive.com.mp4"
    #Crop image to target output size
    subprocess.run([
        "ffmpeg", "-i", backgroundImage, "-vf",
        'scale=854:480:force_original_aspect_ratio=increase,crop=854:480',
        backgroundImageCrop
    ])
    videoExtention = ".mp4"
    intermediateVideo1 = pathlib.Path(
        audio.parents[0], audio.stem + " intermediate1" + videoExtention)
    intermediateVideo2 = pathlib.Path(
        audio.parents[0], audio.stem + " intermediate2" + videoExtention)
    intermediateVideo3 = pathlib.Path(
        audio.parents[0], audio.stem + " intermediate3" + videoExtention)
    intermediateVideo4 = pathlib.Path(
        audio.parents[0], audio.stem + " intermediate4" + videoExtention)
    intermediateVideo5 = pathlib.Path(
        audio.parents[0], audio.stem + " intermediate5" + videoExtention)
    output = pathlib.Path(audio.parents[0], audio.stem + videoExtention)
    #Loop image to be length of audio
    subprocess.run([
        "ffmpeg", "-loop", "1", "-y", "-i", backgroundImageCrop, "-i", audio,
        "-shortest", "-acodec", "copy", "-vcodec", "mjpeg", "-q:v", "3",
        intermediateVideo1
    ])
    #Apply grain2 effect
    subprocess.run([
        "ffmpeg", "-i", intermediateVideo1, "-stream_loop", "-1", "-y", "-i",
        grain2, "-shortest", "-filter_complex",
        "[1:v]colorkey=0x000000:0.3:0.7[ckout];[0:v][ckout]overlay[out]",
        "-map", "0:a", "-c:a", "copy", "-map", "[out]", intermediateVideo2
    ])
    #Apply grain1 effect
    subprocess.run([
        "ffmpeg", "-i", intermediateVideo2, "-stream_loop", "-1", "-y", "-i",
        grain1, "-shortest", "-filter_complex",
        "[1:v]colorkey=0x000000:0.2:0.8[ckout];[0:v][ckout]overlay[out]",
        "-map", "0:a", "-c:a", "copy", "-map", "[out]", intermediateVideo3
    ])
    #Apply ripple effect
    subprocess.run([
        "ffmpeg", "-i", intermediateVideo3, "-f", "lavfi", "-i",
        "nullsrc=s=854x480,lutrgb=128:128:128", "-f", "lavfi", "-i",
        "nullsrc=s=854x480,geq='r=128+4*sin(2*PI*X/1200+T):g=128+4*sin(2*PI*X/1200+T):b=128+4*sin(2*PI*X/1200+T)'",
        "-lavfi", "[0][1][2]displace", intermediateVideo4
    ])
    #Apply wave effect
    subprocess.run([
        "ffmpeg", "-i", intermediateVideo4, "-f", "lavfi", "-i",
        "nullsrc=854x480,geq='r=128+4*(sin(sqrt((X-W/2)*(X-W/2)+(Y-H/2)*(Y-H/2))/920*2*PI+T)):g=128+4*(sin(sqrt((X-W/2)*(X-W/2)+(Y-H/2)*(Y-H/2))/920*2*PI+T)):b=128+4*(sin(sqrt((X-W/2)*(X-W/2)+(Y-H/2)*(Y-H/2))/920*2*PI+T))'",
        "-lavfi", "[1]split[x][y],[0][x][y]displace", intermediateVideo5
    ])
    #Apply chromatic distortion
    subprocess.run([
        "ffmpeg", "-i", intermediateVideo5, "-vf",
        "rgbashift=rh=3:bh=-4:gv=-1", output
    ])
    #Delete intermediate files
    backgroundImageCrop.unlink()
    intermediateVideo1.unlink()
    intermediateVideo2.unlink()
    intermediateVideo3.unlink()
    intermediateVideo4.unlink()
    intermediateVideo5.unlink()
    return


def validateInput():
    # Ensure file was passed as input
    try:
        fileInput = sys.argv[1]
        return fileInput
    except IndexError:
        print("No input file provided!")
        exit()


def copyExports(tmpDir, input):
    # Copy completed audio and video exports from temp directory to input file location
    destinationDir = str((pathlib.Path(input)).parents[0])
    copy_tree(tmpDir, destinationDir)
    return


if __name__ == '__main__':
    print("Starting up.")
    tmpDirectory = tempfile.mkdtemp()
    inputFile = validateInput()
    outputAudio = effects(inputFile, tmpDirectory)
    createVideo(outputAudio, tmpDirectory)
    copyExports(tmpDirectory, inputFile)
    print("Audio and video files created! Cleaning up.")
    shutil.rmtree(tmpDirectory)
    print("Cleanup complete.")
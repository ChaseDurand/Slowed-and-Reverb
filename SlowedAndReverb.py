from logging import error
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
    tag = " [Slowed and Reverb]"
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
    backgroundImageBlur = pathlib.Path(tmpDirectory,
                                       "backgroundImageBlur" + ".jpg")
    grain = "media/grain/VHS Rewind Grain Overlay Effect - freestockfootagearchive.com.mp4"
    subprocess.run([
        "ffmpeg", "-i", backgroundImage, "-vf",
        'scale=854:480:force_original_aspect_ratio=increase,crop=854:480',
        backgroundImageBlur
    ])
    #TODO add moving noise
    videoExtention = ".mov"
    tag = " [Slowed and Reverb]"
    intermediateVideo = pathlib.Path(
        audio.parents[0], audio.stem + " intermediate" + tag + videoExtention)
    output = pathlib.Path(audio.parents[0], audio.stem + tag + videoExtention)
    subprocess.run([
        "ffmpeg", "-loop", "1", "-y", "-i", backgroundImageBlur, "-i", audio,
        "-shortest", "-acodec", "copy", "-vcodec", "mjpeg", "-q:v", "3",
        intermediateVideo
    ])
    subprocess.run([
        "ffmpeg", "-i", intermediateVideo, "-i", grain, "-filter_complex",
        "[1:v]colorkey=0x000000:0.3:0.7[ckout];[0:v][ckout]overlay[out]",
        "-map", "[out]", output
    ])
    #Delete blurred background image
    backgroundImageBlur.unlink()
    intermediateVideo.unlink()
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
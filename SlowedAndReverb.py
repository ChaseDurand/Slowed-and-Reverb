from os import pardir
import subprocess
import sys
import pathlib
import tempfile
import shutil
import random
from distutils.dir_util import copy_tree


def effects(input, tmpDirectory):
    # Apply resampling and convolution reverb to audio file
    # Because this uses filter and filter_complex, effects need to be done in 2 separate ffmpeg processes
    # Resample to 44100 to ensure
    # Append output file with tag.
    pathInput = pathlib.Path(input)
    inputName = pathInput.stem
    extention = pathInput.suffix
    tmpName1 = " Resampled"
    tmpName2 = " Slowed"
    tag = " [Slowed and Reverb]"
    speed = 0.73
    sampleRate = round(44100 * speed)
    sampleRateCommand = "asetrate=" + str(sampleRate)
    intermediateAudio1 = pathlib.Path(tmpDirectory,
                                      inputName + tmpName1 + extention)
    intermediateAudio2 = pathlib.Path(tmpDirectory,
                                      inputName + tmpName2 + extention)
    finalAudio = pathlib.Path(tmpDirectory, inputName + tag + extention)
    #TODO figure out how to determine this to skip in 99% of situations
    subprocess.run(["ffmpeg", "-i", input, "-ar", "44100",
                    intermediateAudio1])  # Convert input file to 44100Hz
    subprocess.run([
        "ffmpeg", "-i", input, "-filter:a", sampleRateCommand, "-ar", "44100",
        intermediateAudio2
    ])  # Slow audio and resample to 44100Hz
    subprocess.run([
        "ffmpeg", "-i", intermediateAudio2, "-i", "media/impulse.wav",
        "-filter_complex", "[0] [1] afir=dry=10:wet=10", finalAudio
    ])  # Apply convolution reverb

    #Delete intermediate files
    intermediateAudio1.unlink()
    intermediateAudio2.unlink()
    return finalAudio


def createVideo(audio):
    # Create a video file using audio track and images
    # Get a random background image from background folder
    backgroundImage = random.choice(
        list(pathlib.Path("media/background/").rglob('*jpg')))
    videoExtention = ".mov"
    tag = " [Slowed and Reverb]"
    output = pathlib.Path(audio.parents[0], audio.stem + tag + videoExtention)
    subprocess.run([
        "ffmpeg", "-loop", "1", "-y", "-i", backgroundImage, "-i", audio,
        "-shortest", "-acodec", "copy", "-vcodec", "mjpeg", "-q:v", "3", output
    ])
    return


def validateInput():
    # Ensure file was passed as input
    # Check if input file is valid audio file
    try:
        fileInput = sys.argv[1]
        #TODO validate mp3
        return fileInput
    except IndexError:
        print("No input file provided!")


def copyExports(tmpDir, input):
    # Copy completed audio and video exports from temp directory to input file location
    destinationDir = str((pathlib.Path(input)).parents[0])
    copy_tree(tmpDir, destinationDir)
    return


if __name__ == '__main__':
    print("Starting up:")
    tmpDirectory = tempfile.mkdtemp()
    inputFile = validateInput()
    outputAudio = effects(inputFile, tmpDirectory)
    createVideo(outputAudio)
    copyExports(tmpDirectory, inputFile)
    shutil.rmtree(tmpDirectory)
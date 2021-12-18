import subprocess
import sys
import pathlib
import uuid
import tempfile
import shutil


def effects(input):
    #TODO basic security of subprocess
    pathInput = pathlib.Path(input)
    fileLocation = pathInput.parents[0]
    inputName = pathInput.stem
    extention = pathInput.suffix
    tmpName = uuid.uuid4().hex
    tmpFileLocation = tempfile.mkdtemp()
    tmpPath = pathlib.Path(tmpFileLocation, tmpName + extention)
    tmpFinal = pathlib.Path(tmpFileLocation,
                            tmpName + " [Slowed and Reverb]" + extention)
    outputPath = pathlib.Path(fileLocation,
                              inputName + " [Slowed and Reverb]" + extention)

    #TODO consolidate these processes
    #TODO determine sample rate as multiple of input file rate, not fixed rate
    subprocess.run(
        ["ffmpeg", "-i", input, "-filter:a", "asetrate=32000", tmpPath])
    #TODO write to temp file then copy on completion
    subprocess.run([
        "ffmpeg", "-i", tmpPath, "-i", "impulse.wav", "-filter_complex",
        "[0] [1] afir=dry=10:wet=10", tmpFinal
    ])
    shutil.copy(tmpFinal, outputPath)
    #TODO resample audio to original sample rate
    shutil.rmtree(tmpFileLocation)
    return


def validateInput():
    try:
        fileInput = sys.argv[1]
        #TODO validate mp3
        return fileInput
    except IndexError:
        print("No input file provided!")


if __name__ == '__main__':
    print("Starting up:")
    outputAudio = effects(validateInput())
    #TODO Get file sample rate
    #TODO Select art
    #TODO Generate video
    #TODO Export
import subprocess
import sys
import pathlib
import uuid


def effects(input):
    #TODO basic security of subprocess
    pathInput = pathlib.Path(input)
    fileLocation = pathInput.parents[0]
    inputName = pathInput.stem
    extention = pathInput.suffix
    tmpName = uuid.uuid4().hex
    tmpPath = pathlib.Path(fileLocation, tmpName + extention)
    outputPath = pathlib.Path(fileLocation,
                              inputName + " [Slowed and Reverb]" + extention)
    print(tmpPath)
    #TODO consolidate these processes
    subprocess.run(
        ["ffmpeg", "-i", input, "-filter:a", "asetrate=32000", tmpPath])
    subprocess.run([
        "ffmpeg", "-i", tmpPath, "-i", "impulse.wav", "-filter_complex",
        "[0] [1] afir=dry=10:wet=10", outputPath
    ])
    tmpPath.unlink()
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
    # slow(validateInput)
    #TODO Get file sample rate
    #TODO Get file metadata
    #TODO Select art
    #TODO Generate video
    #TODO Export
#ffmpeg -r 1 -i img%01d.png -vcodec mpeg4 -y movie.mp4

#gopro get image and make timelapse

# Connect wifi to gopro before running the script

from ffmpeg import FFmpeg
from goprocam import GoProCamera, constants
from pathlib import Path
import json
import os
current_dir = Path(__file__).parent

connect_camera = True
make_movie = False

def main():
    print("Downloading files from GoPro")

    for dir in list(current_dir.glob('*/')):
        if len(list(dir.glob("*.mp4"))) > 0:
            continue
        else:
            found_empty_dir = True
            # take current dir as lapsedir
        
    if found_empty_dir:
        os.chdir(dir)
    else:
        os.mkdir(current_dir / f"Timelapse {len(list(current_dir.glob('*/')))}") 
        os.chdir(current_dir / f"Timelapse {len(list(current_dir.glob('*/')))}")  
        

    try:
        if not connect_camera:
            raise Exception("No camera")
        goproCamera = GoProCamera.GoPro()
        if goproCamera._camera == "":
           raise Exception("No camera found")
        found_empty_dir = False
        
        data = json.loads(goproCamera.listMedia())
        lapsefolder = data['media'][-1]['d']
        lapsefile = data['media'][-1]['fs'][0]['n']
        goproCamera.downloadMultiShot(f"{lapsefolder}/{lapsefile}")
    except Exception as e:
        print(f"Exception: {e}")
    start_frame = int(os.listdir()[0].removeprefix("G").removesuffix(".JPG"))
    if not make_movie:
        print("Not assembling frames");
        exit()
        
    print("Assembling individual frames into MP4")
    Path(os.getcwd())
    ffmpeg = (
        FFmpeg()
        .input("G%7d.JPG", start_number=start_frame)
        .output('movie.mp4')
    )

    ffmpeg.execute()
    print(f"Output ready at: f{os.getcwd()}/movie.mp4")

if __name__ == "__main__":
    main()
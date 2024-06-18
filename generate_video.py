#ffmpeg -r 1 -i img%01d.png -vcodec mpeg4 -y movie.mp4

#gopro get image and make timelapse

# Connect wifi to gopro before running the script

from ffmpeg import FFmpeg
from goprocam import GoProCamera, constants
from pathlib import Path
import json
import os
class GenerateVideo:
    current_dir = Path(__file__).parent

    connect_camera = True
    make_movie = True
    gopro_file = ""
    gopro_dir = ""
    number_of_frames = 0
    timelapse_dir = None

    def verify_files(self, folder, gopro_filenames):
        frames = [i.name for i in folder.glob("*.JPG")]
        for file in gopro_filenames:
            if file not in frames:
                print(f"Missing {file} in folder")
                return file
        print("All files are present")
        return None

    def main(self):
        print("Downloading files from GoPro")
        found_empty_dir = False

        # find empty directory that has not been timelapsed yet
        # TODO: Improve behavior, we dont want to create duplicate folders
        for timelapse_dir in list(self.current_dir.glob('*/')):

            if "Timelapse" not in timelapse_dir.name:
                continue
            elif len(list(timelapse_dir.glob("*.mp4"))) > 0:
                continue
            else:
                found_empty_dir = True
                break
                # take current dir as lapsedir
            
        if found_empty_dir:
            self.timelapse_dir = timelapse_dir
            os.chdir(self.timelapse_dir)
        else:
            folder_number = len(list(self.current_dir.glob('Timelapse */')))
            self.timelapse_dir = self.current_dir / f"Timelapse {folder_number}"
            os.mkdir(self.timelapse_dir) 
            os.chdir(self.timelapse_dir)  
            

        try:
            if not self.connect_camera:
                raise Exception("No camera")
            goproCamera = GoProCamera.GoPro()
            if goproCamera._camera == "":
                raise Exception("No camera found")
            if goproCamera.getStatus(constants.Status.Status, constants.Status.STATUS.IsBusy):
                raise Exception("Camera is busy")
            data = " "
            # timelapse frames are split in batches of 999 pictures
            while True:
                data = json.loads(goproCamera.listMedia())
                if len(data['media']) == 0:
                    break
                # select last data to download
                # TODO: do not select videos
                self.gopro_dir = data['media'][-1]['d']
                self.gopro_file = data['media'][-1]['fs'][0]['n']
                upper_bound = int(data['media'][-1]['fs'][0]['l'])
                lower_bound = int(data['media'][-1]['fs'][0]['b'])
                self.number_of_frames = upper_bound - lower_bound + 1
                print(f"Item {self.gopro_file} has {self.number_of_frames} files")
                # create list of names in this timelapse batch
                gopro_filenames = list(self.gopro_file[:4] + str(lower_bound + i).zfill(4) + ".JPG" for i in range(upper_bound - lower_bound + 1))

                # check if we already have all files
                file = self.verify_files(self.timelapse_dir, gopro_filenames)
                if file is not None:
                    # adjust number of missing frames
                    self.number_of_frames = upper_bound - lower_bound + 1 - gopro_filenames.index(file)
                    print(f"Downloading missing {self.number_of_frames} files from GoPro (This can take a while)")
                    if(self.number_of_frames != len(gopro_filenames) - gopro_filenames.index(file)):
                        print(f"something going wrong, found {self.number_of_frames} frames to download, and {len(gopro_filenames) - gopro_filenames.index(file)} frames needed")
                    for i in range(gopro_filenames.index(file), gopro_filenames.index(file) + self.number_of_frames):
                        goproCamera.downloadMedia(self.gopro_dir, gopro_filenames[i])
                    #verify all files were downloaded
                    if self.verify_files(self.timelapse_dir, gopro_filenames) is not None:
                        raise Exception("Not all files were downloaded")
                    
# -- from here on, we need to check again
                print("All files downloaded, delete from GoPro")
                print()
                for i, frame in enumerate(gopro_filenames):
                    response = goproCamera.deleteFile(self.gopro_dir, frame)
                    print(f"\rDeleting {frame}, {i+1:02d}/{self.number_of_frames:02d}\r", end="")
                    if response == "":
                        print(f"Already deleted {frame}           ")
                print()
                print("Deleted timelapse frames from GoPro")

        except Exception as e:
            print(f"Exception: {e}")
            exit()
        print()

        start_frame = int(os.listdir()[0].removeprefix("G").removesuffix(".JPG"))
        if not self.make_movie:
            print("Not assembling frames")
            exit()
            
        print("Assembling individual frames into MP4 (this can take a while)")
        Path(os.getcwd())
        ffmpeg = (
            FFmpeg()
            .input("G%7d.JPG", start_number=start_frame)
            .output('movie.mp4')
        )

        ffmpeg.execute()
        print(f"Output ready at: f{os.getcwd()}/movie.mp4")

if __name__ == "__main__":
    script = GenerateVideo()
    script.main()
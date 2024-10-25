# Youtube
# from pytubefix import YouTube
from pytubefix import YouTube

# from pytube import YouTube || Note, currently not working, so 'pytubefix' is the temporary solution.

import os
import re
import subprocess

# Audio
import io
from pydub import AudioSegment

# Data
import pandas as pd


from moviepy.editor import VideoFileClip, AudioFileClip

from media_types import JRE, Interview, SpeechDataset, Music


CLIENTS = {
    1: "WEB",
    2: "WEB_EMBED",
    3: "WEB_MUSIC",
    4: "WEB_CREATOR",
    5: "WEB_SAFARI",
    6: "ANDROID",
    7: "ANDROID_MUSIC",
    8: "ANDROID_CREATOR",
    9: "ANDROID_VR",
    10: "ANDROID_PRODUCER",
    11: "ANDROID_TESTSUITE",
    12: "IOS",
    13: "IOS_MUSIC",
    14: "IOS_CREATOR",
    15: "MWEB",
    16: "TV_EMBED",
    17: "MEDIA_CONNECT",
}


audio_settings = {
    "params": {"adaptive": True, "file_extension": "wav", "only_audio": True}
}

video_settings = {
    "params": {"adaptive": True, "file_extension": "mp4", "only_video": True},
    "order_by": "resolution",  # or any other attribute you want to order by
}


class YouTubeDownloader:
    def __init__(
        self,
        url: str,
        client_type: str,
        bypass_age: bool = False,
        replace_url: bool = True,
    ) -> None:
        self.client_types = ["MWEB", "WEB", "WEB_CREATOR", "WEB_EMBED"]
        if replace_url:
            url = self.replace_url(url)
        self.url = url
        self.yt = YouTube(
            url, client="ANDROID", use_oauth=False, allow_oauth_cache=True
        )
        if bypass_age:
            self.yt.bypass_age_gate()

    def replace_url(self, url: str) -> str:
        """Occasionally, YouTube will have issues downloading the video.
        A workaround is to replace the 'watch?v=' with 'embed/'.

        Parameters
        ----------
        url : str
            Url to be converted.

        Returns
        -------
        str
            Converted url.
        """
        pattern = r"watch\?v=|&t=\d+s?"
        # Replace 'watch?v=' with 'embed/'
        converted_url = re.sub(pattern, "embed/", url)

        return converted_url

    def download_video(self, export_path: str, file_name: str = ""):
        """
        Download the video in mp4 format. Does not include audio.

        Parameters
        ----------
        export_path : str
            Folder to export file to.
        file_name : str, optional
            Name of the file being saved. *NOTE* Include extension, by default "video.mp4"


        """
        # Download video (without audio)
        video_stream = (
            self.yt.streams.filter(adaptive=True, file_extension="mp4", only_video=True)
            .order_by("resolution")
            .desc()
            .first()
        )

        if file_name == "":
            file_name = "video"

        video_stream.download(
            output_path=export_path,
            filename=f"{file_name}.mp4",
        )

    def download_audio(self, export_path: str, file_name: str = ""):
        """
        Download the audio for the video. Saves in '.wav' format.

        Parameters
        ----------
        export_path : str
            Folder to export file to.
        file_name : str, optional
            Name of the file being saved, by default "audio.wav"

        Returns
        -------
        _type_
            _description_
        """
        # Download audio (without video)
        audio_stream = self.yt.streams.filter(
            only_audio=True, file_extension="mp4"
        ).first()
        if file_name == "":
            file_name = "audio"

        audio_data = io.BytesIO()
        audio_stream.stream_to_buffer(audio_data)
        audio_data.seek(0)
        audio = AudioSegment.from_file(audio_data, format="mp4")
        path = f"{export_path}\\{file_name}.wav"
        audio.export(path, format="wav")
        return audio

    def get_captions(self) -> pd.DataFrame:
        """
        Get Auto-Generated captions provided by YouTube.

        Returns
        -------
        DataFrame
            Dataframe containing text and timestamps.
        """
        try:
            captions = self.yt.caption_tracks[0]
        except IndexError:
            captions = self.yt.captions
            print(f"Captions: {captions}\nCaptions not available for '{self.yt.title}'")
            exit()
        captions = captions.generate_srt_captions()
        captions = captions.split("\n")
        cur_index = 0
        cols = ["index", "timestamp", "text"]
        data = {"index": [], "start": [], "end": [], "text": []}
        for c in captions:

            if c == "":
                pass
                cur_index = 0
            else:
                col = cols[cur_index]
                if col == "timestamp":
                    start, end = c.split("-->")
                    start = start.strip(" ").replace(",", ".")
                    end = end.strip(" ").replace(",", ".")
                    start_ms = self._time_to_milliseconds(start)
                    end_ms = self._time_to_milliseconds(end)
                    duration = end_ms - start_ms
                    duration = duration / 2
                    new_end_ms = start_ms + duration
                    end = self._milliseconds_to_time(new_end_ms)

                    data["start"].append(start)
                    data["end"].append(end)

                else:
                    data[col].append(c)
                cur_index += 1

        df = pd.DataFrame(data)
        df.drop("index", axis=1, inplace=True)
        return df

    def get_laugther_clips(
        self,
        source_video_path: str,
        export_path: str,
        source_audio_path: str = "",
        peripheral_seconds: int = 30,
    ):

        video = VideoFileClip(source_video_path)
        video_duration = video.duration
        if source_audio_path != "":
            audio = AudioFileClip(source_audio_path)
            video = video.set_audio(audio)
            include_audio = True
        else:
            include_audio = False

        timestamps = self.get_laughter_timestamps()

        clip = 1
        for i, row in timestamps.iterrows():
            anchor_time = self._time_to_seconds(row["start"])

            clip_start = anchor_time - peripheral_seconds
            clip_end = anchor_time + peripheral_seconds

            if clip_start < 0:
                clip_start = 0

            if clip_end > video_duration:
                clip_end = video_duration
            subclip = video.subclip(clip_start, clip_end)
            subclip_path = f"{export_path}/clip_{clip}.mp4"
            subclip.write_videofile(subclip_path, codec="libx264", audio=include_audio)
            clip += 1

    def get_laughter_timestamps(self):
        captions = self.get_captions()
        laughter = captions[captions["text"] == "[Laughter]"]
        return laughter

    def _time_to_milliseconds(self, t) -> int:
        """
        Function to convert HH:MM:SS.MMM to milliseconds

        t: str
            String of a timestamp.

        returns: int
            Integer representing the timestamp in milliseconds.
        """
        try:
            h, m, s = t.split(":")
            s, ms = s.split(".")
            return (int(h) * 3600 + int(m) * 60 + int(s)) * 1000 + int(ms)
        except ValueError:
            h, m, s, ms = t.split(":")
            return (int(h) * 3600 + int(m) * 60 + int(s)) * 1000 + int(ms)

    def _milliseconds_to_time(self, ms):
        """
        Function to convert HH:MM:SS.MMM to milliseconds

        ms: int
            Integer representing a timestamp in milliseconds.

        returns: str
            String representing 'ms' as a timestamp.
        """
        # Calculate hours, minutes, and seconds
        seconds, milliseconds = divmod(ms, 1000)
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        # Format the time as HH:MM:SS.sss
        time_str = f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}.{int(milliseconds):03}"
        return time_str

    def _time_to_seconds(self, t):
        h, m, s = map(float, t.split(":"))
        return h * 3600 + m * 60 + s


def convert_to_wav(file_path: str, wav_file_path: str):
    extension = file_path.split(".")[-1]
    # Load the audio from the MP4 file
    audio = AudioSegment.from_file(file_path, format=extension)

    # Export the audio to a WAV file
    audio.export(wav_file_path, format="wav")


def clip_audio(
    input_file_path: str, output_folder: str, clip_duration: int, clip_name: str
):
    """
    Clips the audio file into segments of specified duration.

    Parameters
    ----------
    input_file_path : str
        Path to the input audio file.
    output_folder : str
        Folder to save the clipped audio files.
    clip_duration : int
        Duration of each clip in seconds.
    """
    # Load the audio file
    audio = AudioSegment.from_file(input_file_path, format="wav")

    # Calculate the number of clips
    total_duration = len(audio)  # in milliseconds
    clip_duration_ms = clip_duration * 1000  # convert seconds to milliseconds

    # Create clips
    for i in range(0, total_duration, clip_duration_ms):
        clip = audio[i : i + clip_duration_ms]
        clip.export(
            f"{output_folder}/{clip_name}_{i // clip_duration_ms + 1}.wav", format="wav"
        )


def convert_mkv_to_wav(input_file_path: str, output_file_path: str):
    """
    Converts an MKV file to a WAV file using ffmpeg.

    Parameters
    ----------
    input_file_path : str
        Path to the input MKV file.
    output_file_path : str
        Path to save the output WAV file.
    """
    try:
        # Run ffmpeg command to convert mkv to wav
        subprocess.run(
            [
                "ffmpeg",
                "-i",
                input_file_path,
                "-vn",  # No video
                "-acodec",
                "pcm_s16le",  # Audio codec
                "-ar",
                "44100",  # Audio sample rate
                "-ac",
                "2",  # Number of audio channels
                output_file_path,
            ],
            check=True,
        )
        print(f"Conversion successful: {output_file_path}")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")


def main(mode, obj, url=""):
    if mode == 1:
        yt = YouTubeDownloader(url, client_type="ANDROID")

        yt.download_audio(obj.get_sub_dir())
        # yt.download_video(obj.get_sub_dir())
    elif mode == 2:
        clip_audio(
            input_file_path="./random/buffet.wav",
            output_folder=path,
            clip_duration=20,
            clip_name="buffet_yahoo",
        )


def download_music(
    song_dir: str,
    full_song: bool = False,
    vocals: bool = False,
    instrumental: bool = False,
):

    music = Music(song_dir)
    yt = YouTubeDownloader(url, client_type="ANDROID")

    if full_song:
        yt.download_audio(music.get_sub_dir(), file_name="full_song")
    if vocals:
        yt.download_audio(music.get_sub_dir(), file_name="vocals")
    if instrumental:
        yt.download_audio(music.get_sub_dir(), file_name="instrumental")


def download_speech(speaker: str, file_name: str):
    speech = SpeechDataset(speaker)
    yt = YouTubeDownloader(url, client_type="ANDROID")
    yt.download_audio(speech.get_sub_dir(), file_name=file_name)


if __name__ == "__main__":

    mode = 1

    # obj = JRE(1554)

    url = "https://www.youtube.com/watch?v=R0GO9vdYvec"
    # obj = SpeechDataset("rogan")
    # obj = Music("In_Da_Club")
    # print(f"Instrumental path: {obj.get_instrumental_path()}")
    # convert_to_wav("D:\\Music\\Otherside\\audio.mp3", "D:\\Music\\Otherside\\audio.wav")
    # download(url, audio_settings, "audio", "wav")
    download_speech("penguinz0", file_name="hurricane_milton")
    # download_music("In_Da_Club", full_song=True)
    # convert_mp4_to_wav(f"{path}.mp4", f"{path}.wav")

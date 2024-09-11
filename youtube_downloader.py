# Youtube
from pytubefix import YouTube

# from pytube import YouTube || Note, currently not working, so 'pytubefix' is the temporary solution.


# Audio
import io
from pydub import AudioSegment

# Data
import pandas as pd

from moviepy.editor import VideoFileClip, AudioFileClip


class YouTubeDownloader:
    def __init__(self, url: str) -> None:
        self.url = url
        self.yt = YouTube(url)

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
            file_name = self.yt.title

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
            file_name = self.yt.title

        audio_data = io.BytesIO()
        audio_stream.stream_to_buffer(audio_data)
        audio_data.seek(0)
        audio = AudioSegment.from_file(audio_data, format="mp4")
        audio.export(f"{export_path}/{file_name}.wav", format="wav")
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


if __name__ == "__main__":
    pass

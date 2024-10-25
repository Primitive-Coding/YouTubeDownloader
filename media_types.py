import os


class Media:
    def __init__(
        self,
        base_dir: str,
        sub_dir: str,
        audio_path: str,
        video_path: str,
        transcript_path: str,
    ) -> None:
        self.base_dir = base_dir
        self.sub_dir = sub_dir
        self.audio_path = audio_path
        self.video_path = video_path
        self.transcript_path = transcript_path

    def get_audio_path(self):
        return self.audio_path

    def get_video_path(self):
        return self.video_path

    def get_transcript_path(self):
        return self.transcript_path

    def get_base_dir(self):
        return self.base_dir

    def get_sub_dir(self):
        return self.sub_dir


class JRE(Media):
    def __init__(self, episode_num: int) -> None:
        self.base_dir = "D:\\ML_DATASETS\\podcasts\\JRE"
        self.sub_dir = f"{self.base_dir}\\{episode_num}"
        os.makedirs(self.sub_dir, exist_ok=True)
        self.audio_path = f"{self.sub_dir}\\audio.wav"
        self.video_path = f"{self.sub_dir}\\video.mp4"
        self.transcript_path = f"{self.sub_dir}\\transcript.csv"

        self.guests = {
            1315: "Bob Lazar",
            1470: "Elon Musk",
            1554: "Kanye West",
            2044: "Sam Altman",
            2054: "Elon Musk",
        }

        super().__init__(
            self.base_dir,
            self.sub_dir,
            self.audio_path,
            self.video_path,
            self.transcript_path,
        )


class Interview(Media):
    def __init__(self, interview_subject: str, interview_name: str) -> None:
        self.base_dir = "D:\\ML_DATASETS\\interviews"
        self.sub_dir = f"{self.base_dir}\\{interview_subject}\\{interview_name}"
        os.makedirs(self.sub_dir, exist_ok=True)
        self.audio_path = f"{self.sub_dir}\\audio.wav"
        self.video_path = f"{self.sub_dir}\\video.mp4"
        self.transcript_path = f"{self.sub_dir}\\transcript.csv"
        super().__init__(
            self.base_dir,
            self.sub_dir,
            self.audio_path,
            self.video_path,
            self.transcript_path,
        )


class SpeechDataset(Media):
    def __init__(self, speaker: str) -> None:
        self.base_dir = f"D:\\ML_DATASETS\\custom_tts\\{speaker}"
        self.sub_dir = f"{self.base_dir}"
        os.makedirs(self.sub_dir, exist_ok=True)
        self.audio_path = f"{self.sub_dir}\\audio.wav"
        super().__init__(self.base_dir, self.sub_dir, self.audio_path, None, None)


class Music(Media):
    def __init__(self, song_name: str) -> None:
        self.base_dir = "D:\\ML_DATASETS\\music"
        self.sub_dir = f"{self.base_dir}\\{song_name}"
        os.makedirs(self.sub_dir, exist_ok=True)
        self.audio_path = f"{self.sub_dir}\\audio.wav"
        self.instrumental_path = f"{self.sub_dir}\\instrumental.wav"
        super().__init__(self.base_dir, self.sub_dir, self.audio_path, None, None)

    def get_instrumental_path(self):
        return self.instrumental_path

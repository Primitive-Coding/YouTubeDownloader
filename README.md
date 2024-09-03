# YouTubeDownloader

- Easily download audio, video, and transcript data.

### Setup

1. Clone git repository: `https://github.com/Primitive-Coding/YouTubeDownloader.git`
2. Install the projects requirements with `pip install -r requirements.txt`

### Instructions

- Create a class instance

```
    yt = YouTubeDownloader('url')
```

##### Download Audio

- Download audio data from the video associated with the url.
  - `export_path` is the path to the folder where the file will be saved.
  - `file_name` is the name of the file to be saved. **NOTE** Make sure to include `.wav` extension.

```
    yt.download_audio(export_path, file_name)
```

##### Download Video

- Download video data from the video associated with the url.
  - `export_path` is the path to the folder where the file will be saved.
  - `file_name` is the name of the file to be saved. **NOTE** Make sure to include `.mp4` extension.

```
    yt.download_video(export_path, file_name)
```

##### Captions

- Get transcripts for the video with timestamps.

```
    df = yt.get_captions()


    print(df)

        start           end                                    text
0    00:00:24.439  00:00:28.199  okay looks like 2015 is when they were
1    00:00:28.679  00:00:30.319                    founded sounds right
2    00:00:35.000  00:00:37.320                       so we're 10 years
3    00:00:36.559  00:00:39.259                     into this company's
4    00:00:39.640  00:00:41.660  existence we can skip the risk factors
..            ...           ...                                     ...
832  00:47:23.400  00:47:26.879                     829 and using it on
833  00:47:25.680  00:47:30.119     31491 with 127 to the 8,694 minus 1
834  00:47:30.359  00:47:35.034  gives a common factor of 379 and 829 *
835  00:47:34.559  00:47:41.244         379 does indeed give us 314,000
836  00:47:39.710  00:47:43.819                                 [Music]
```

from yupload import YouTubeUploader

uploader = YouTubeUploader(
    'data/test.mp4',
    title="Test",
    description="Test Description"
)
was_video_uploaded, video_id = uploader.upload()
assert was_video_uploaded

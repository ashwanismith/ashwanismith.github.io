from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound, VideoUnavailable
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def extract_video_id(url: str) -> str:
    if "youtu.be" in url:
        return url.split("/")[-1]
    elif "v=" in url:
        return url.split("v=")[-1].split("&")[0]
    else:
        return ""

@app.get("/transcript")
async def get_transcript(request: Request):
    url = request.query_params.get("url")
    video_id = extract_video_id(url)

    if not video_id:
        return JSONResponse(content={"error": "Invalid YouTube URL"}, status_code=400)

    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        full_text = " ".join([entry['text'] for entry in transcript])
        return {"transcript": full_text}

    except TranscriptsDisabled:
        return JSONResponse(content={"error": "Transcripts are disabled for this video."}, status_code=403)
    except NoTranscriptFound:
        return JSONResponse(content={"error": "No transcript found for this video."}, status_code=404)
    except VideoUnavailable:
        return JSONResponse(content={"error": "Video is unavailable."}, status_code=404)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)


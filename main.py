import json
from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel
import llm_cafe

app = FastAPI()

BASE_DIR = Path(__file__).parent
PROFILE_PATH = BASE_DIR / "profile.json"
DEFAULT_PROFILE = {"walk": 4.5, "jog": 8.0, "run": 12.0, "sprint": 12.0, "measured": []}

# 1. AI 챗봇 요청 규격
class ChatRequest(BaseModel):
    query: str
    area: str = "대전 유성구 궁동/어은동"

# 2. 걸음속도 프로필 저장 규격 (준영 파트 연동)
class SpeedProfile(BaseModel):
    walk: float
    jog: float = 0.0
    run: float = 0.0
    sprint: float = 0.0
    measured: list = []

# 메인 웹 화면(index.html) 제공
@app.get("/")
def serve_home():
    return FileResponse("index.html")

# [파트 1] 개인 걸음속도 조회 & 저장 API
@app.get("/api/profile")
def get_profile():
    if PROFILE_PATH.exists():
        return json.loads(PROFILE_PATH.read_text(encoding="utf-8"))
    return DEFAULT_PROFILE

@app.post("/api/profile")
def save_profile(profile: SpeedProfile):
    data = profile.model_dump()
    # 변수명 차이(jog vs run / run vs sprint) 자동 동기화
    if data["jog"] == 0.0 and data["run"] > 0.0:
        data["jog"] = data["run"]
    if data["sprint"] == 0.0 and data["run"] > 0.0:
        data["sprint"] = data["run"]
    PROFILE_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"status": "ok", "profile": data}

# [파트 3] LLM 카페 추천 API
@app.post("/api/recommend")
def api_recommend(req: ChatRequest):
    if hasattr(llm_cafe, "recommend_cafes"):
        result = llm_cafe.recommend_cafes(req.query, req.area)
    else:
        single = llm_cafe.recommend_cafe(req.query, req.area)
        result = {"cafes": [single]} if "name" in single else single
    return result
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
from fastapi import FastAPI

from backend.skill_proficiency.routes.analyze import router as analyze_router


app = FastAPI(title="Skill Proficiency Analyzer", version="1.0.0")
app.include_router(analyze_router)

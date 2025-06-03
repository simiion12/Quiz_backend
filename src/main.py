from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.routes.grade_routes import router as grade_routes
from src.routes.course_routes import router as course_routes
from src.routes.quiz_routes import router as quiz_routes
from src.routes.user_routes import router as user_routes
from src.routes.s3_routes import router as s3_routes
from src.auth.router import router as auth_router


app = FastAPI()

origins = [
    "http://localhost:3000",
    "http://localhost:8080",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8080",
]

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(grade_routes)
app.include_router(course_routes)
app.include_router(quiz_routes)
app.include_router(user_routes)
app.include_router(s3_routes)

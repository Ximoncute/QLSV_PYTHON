# Version 3.0.3 - Reload Trigger
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend1.db.session import engine, Base
from backend1.core.exceptions import setup_exception_handlers
from backend1.routers import auth, admission, admin, student, graduation, notifications, stats

# Create database tables
Base.metadata.create_all(bind=engine)

print("DEBUG_BACKEND: Initializing FastAPI App...")
app = FastAPI(
    title="University Management API",
    description="Professional Backend for Student Management System.",
    version="3.0.2",
)
print(f"DEBUG_BACKEND: App created. Base routes: {[r.path for r in app.routes]}")

# 1. Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Setup Exception Handlers
setup_exception_handlers(app)

# 3. Register Routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(stats.router, prefix="/quan-tri", tags=["Statistics"])
app.include_router(admin.router, prefix="/quan-tri", tags=["Admin Operations"])
app.include_router(admin.router, prefix="", tags=["Academic CRUD"]) 
app.include_router(student.router, prefix="/sinh-vien", tags=["Student Portal"])
app.include_router(student.router, prefix="/hoc-tap", tags=["Grades"]) 
app.include_router(admission.router, prefix="/admission", tags=["Admissions"])
app.include_router(graduation.router, prefix="/tot-nghiep", tags=["Graduation"])
app.include_router(notifications.router, prefix="/thong-bao", tags=["Notifications"])

print(f"DEBUG_BACKEND: All routers included. Registered routes count: {len(app.routes)}")
print(f"DEBUG_BACKEND: Registered paths: {[r.path for r in app.routes]}")

@app.get("/debug/routes")
def list_routes():
    return [{"path": route.path, "name": route.name, "methods": list(route.methods)} for route in app.routes]

@app.get("/")
def welcome():
    return {"message": "Backend Online", "docs": "/docs"}

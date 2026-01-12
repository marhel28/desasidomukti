from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from db.main import init_db
from auth.route import router_user

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     print("\n\nServer has started...\n\n")
#     await init_db()
#     yield
#     print("\n\nServer has stopped...\n\n")
    
    
app = FastAPI(
    debug=True,
    title="Aplikasi marketplace",
    description="Aplikasi pengelolaan penjualan  ",
    # lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      
    allow_credentials=False, 
    allow_methods=["*"],      
    allow_headers=["*"],     
)


app.include_router(router_user,prefix="/api/v1",tags=['auth'])
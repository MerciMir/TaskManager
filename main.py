# main.py
from fastapi import FastAPI, Depends, HTTPException, Request, Response, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from database.db import Base, engine, get_db
from users.models import User
from tasks.models import Task
from users.schemas import UserRegister, UserLogin
from tasks.shcemas import TaskCreate
from auth import create_access_token, decode_token
from websocket_manager import manager
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins={"http://127.0.0.1:5500"},
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
Base.metadata.create_all(bind=engine)


# Регистрация пользователя
@app.post("/register")
def register(user: UserRegister, response: Response, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.login == user.login).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Login already registered")
    new_user = User(name = user.name, login=user.login, password=user.password, role=user.role)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    access_token = create_access_token(data={"sub": str(new_user.id)})


    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=1800,
        expires=1800,
        secure=True, 
        samesite="lax"
    )
    return {"message": "User created successfully"}

# Логин пользователя
@app.post("/login")
def login(user: UserLogin, response: Response, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.login == user.login).first()
    if not db_user or db_user.password != user.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_access_token(data={"sub": str(db_user.id)})
    
    response.set_cookie(
        key="access_token",
        value=access_token,
        expires=1800,
    )
    return {"access_token": access_token}

@app.get("/logout")
def delete_cookie(response: Response):
    response.delete_cookie(key="access_token")
    return {"message": "Cookie has been deleted"}

@app.get("/my-role")
def get_my_role(request: Request, db: Session = Depends(get_db)):
    # Получаем токен из куки
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    # Убираем "Bearer " из токена
    token = token.replace("Bearer ", "")

    # Декодируем токен
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    # Получаем user_id из токена
    user_id = int(payload.get("sub"))
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    # Получаем пользователя из базы данных
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {"role": user.role}

# Создание задачи (доступно только для руководителя)
@app.post("/tasks")
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    new_task = Task(
        title=task.title,
        description=task.description,
        employee_id=task.employee_id,
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    manager.send_notification(task.employee_id, f"New task: {task.title}")

    return new_task

@app.get("/tasks")
def get_tasks(db: Session = Depends(get_db)):
    tasks = db.query(Task).all()
    return tasks

@app.get("/my-tasks")
def get_my_tasks(request: Request, db: Session = Depends(get_db)):

    # Получаем токен из куки
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    # Убираем "Bearer " из токена
    token = token.replace("Bearer ", "")

    # Декодируем токен
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    # Получаем user_id из токена
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    # Получаем задачи, где assigned_to совпадает с user_id
    tasks = db.query(Task).filter(Task.employee_id == user_id).all()
    return tasks

# WebSocket endpoint для уведомлений
@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    await manager.connect(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_text()
            print(f"Received message from user {user_id}: {data}")
    except WebSocketDisconnect:
        manager.disconnect(user_id)
        print(f"User {user_id} disconnected")
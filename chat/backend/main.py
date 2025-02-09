import asyncio

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.messages import HumanMessage
from chat.backend.model import agent
from chat.backend.manager import ConnectionManager

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


manager = ConnectionManager()


@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await manager.connect(websocket, session_id)
    try:
        while True:
            message = await asyncio.wait_for(websocket.receive_text(), timeout=60)

            try:
                # Process with LangGraph
                response = agent.invoke(
                    {
                        "messages": [HumanMessage(content=message)],
                    }
                )
                last_message = response["messages"][-1].content

            except Exception as ex:
                print(ex)
                last_message = "Não foi possível obter uma resposta."

            await websocket.send_text(last_message)

    except asyncio.TimeoutError as te:
        print(te)
        manager.disconnect(session_id)
    except WebSocketDisconnect as wd:
        print(wd)
        manager.disconnect(session_id)
    except Exception as ex:
        print(ex)
        manager.disconnect(session_id)
        await websocket.close()

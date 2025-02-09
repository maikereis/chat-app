import asyncio

import streamlit as st
import websockets.client as websockets

ENDPOINT = "ws://localhost:8000/ws/"


async def send_message(message: str, session_id: str) -> str:
    uri = ENDPOINT + session_id
    try:
        async with websockets.connect(
            uri, ping_interval=None, close_timeout=1
        ) as websocket:
            await websocket.send(message)
            return await websocket.recv()
    except Exception as e:
        return f"Error: {str(e)}"


def initialize_session():
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(
            hash(str(asyncio.get_event_loop_policy().get_event_loop()))
        )
    if "messages" not in st.session_state:
        st.session_state.messages = []


async def main():
    st.title("Converse com uma IA")

    initialize_session()

    # Chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("O que você gostatira de discutir?"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get AI response
        with st.spinner("Aguardando Resposta"):
            response = await send_message(prompt, st.session_state.session_id)

            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": response})
            with st.chat_message("assistant"):
                st.markdown(response)

    # Add a clear chat button
    if st.button("Limpar Chat"):
        st.session_state.messages = []


if __name__ == "__main__":
    asyncio.run(main())

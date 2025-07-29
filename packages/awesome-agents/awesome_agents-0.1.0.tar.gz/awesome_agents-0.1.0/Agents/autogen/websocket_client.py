# import websockets
# import asyncio
#
# async def client():
#     async with websockets.connect("ws://localhost:8000/ws") as websocket:
#         # Send the PDF path
#         await websocket.send("agents.pdf")
#
#         # Receive confirmation
#         response = await websocket.recv()
#         print(response)  # "PDF content processed. You can now ask questions."
#
#         # Ask a question
#         await websocket.send("What is the main topic of the PDF?")
#         response = await websocket.recv()
#         print(response)  # "Assistant: The main topic of the PDF is [topic]."
#
#         # Exit
#         await websocket.send("exit")
#
# asyncio.get_event_loop().run_until_complete(client())

import websockets
import asyncio

async def client():
    try:
        async with websockets.connect("ws://localhost:8000/ws") as websocket:
            print("Connected to the server.")

            # Send the PDF path
            pdf_path = "agents.pdf"  # Ensure this file exists or provide the correct path
            await websocket.send(pdf_path)
            print(f"Sent PDF path: {pdf_path}")

            # Receive confirmation that the PDF has been processed
            response = await websocket.recv()
            print(f"Server response: {response}")  # "PDF content processed. You can now ask questions."

            # Interactive loop to ask questions
            while True:
                # Ask a question
                question = input("Enter your question (or type 'exit' to quit): ")
                await websocket.send(question)

                if question.lower() == "exit":
                    print("Exiting...")
                    break

                # Receive the assistant's response
                response = await websocket.recv()
                print(f"Assistant: {response}")

    except websockets.ConnectionClosedError:
        print("Connection to the server was closed unexpectedly.")
    except Exception as e:
        print(f"An error occurred")


asyncio.run(client())
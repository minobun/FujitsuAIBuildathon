# from openai import OpenAI
# from dotenv import load_dotenv
# import os
# import time
# # .envファイルを読み込む
# load_dotenv()
# # load_dotenv()
# client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# sys_prompt = """
# あなたは日本の関西人です。関西弁で全ての回答をしてください。
# """

# from typing_extensions import override
# from openai import AssistantEventHandler

# def test_assistant():
#     # アシスタントの作成
#     assistant = client.beta.assistants.create(
#         name="Math Tutor",
#         instructions="You are a personal math tutor. Write and run code to answer math questions.",
#         model="gpt-4-1106-preview"
#     )
#     assistant_id = assistant.id
#     print("assistant_id:", assistant_id)

#     # スレッドの作成
#     thread = client.beta.threads.create()
#     thread_id = thread.id
#     print("thread_id:", thread_id)

#     # メッセージの作成
#     message = client.beta.threads.messages.create(
#         thread_id=thread.id,
#         role="user",
#         content="I need to solve the equation `3x + 11 = 14`. Can you help me?"
#     )

#     # スレッドの実行
#     run = client.beta.threads.runs.create(
#         thread_id=thread_id,
#         assistant_id=assistant_id,
#         instructions="Please address the user as Jane Doe. The user has a premium account."
#     )
#     run_id = run.id
#     print("run_id:", run_id)

#     completed = False
#     while not completed:
#         run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)
#         print("run.status:", run.status)
#         if run.status == 'completed':
#             completed = True
#         else:
#             time.sleep(5)

#     # 結果の表示
#     messages = client.beta.threads.messages.list(thread_id=thread_id)

#     print("messages_list:", messages)
#     return messages

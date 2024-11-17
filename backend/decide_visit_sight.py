from fastapi import FastAPI, HTTPException, Query
from openai import OpenAI
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import List, Dict
import googlemaps
import os
import sys
import json
from datetime import datetime
from collections import defaultdict
from fastapi.middleware.cors import CORSMiddleware
import random

# from google.cloud import storage
import requests
from urllib.parse import urlencode

# 標準出力をUTF-8に設定
sys.stdout.reconfigure(encoding="utf-8")
# .envファイルを読み込む
load_dotenv()

# FastAPIインスタンス
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # すべてのオリジンを許可する場合
    allow_credentials=True,
    allow_methods=["*"],  # すべてのHTTPメソッドを許可
    allow_headers=["*"],  # すべてのヘッダーを許可
)

# OpenAIのAPIキーを設定
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Google Maps APIキーを設定
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)

# 対話履歴を保持する辞書 (スレッドIDをキーとする)
thread_histories: Dict[str, List[Dict[str, str]]] = defaultdict(list)


# リクエストモデル
class RouteRequest(BaseModel):
    prompt: str  # generate_responseで使用するプロンプト


# レスポンスモデル
class RouteResponse(BaseModel):
    total_distance: str
    total_duration: str
    optimized_route: List[str]
    detailed_routes: List[dict]  # 各ルートの詳細


def get_directions_api_response(
    api_key, origin, destination, waypoints, departure_time
):
    """
    Google Maps Directions APIを直接たたく関数
    """
    base_url = "https://maps.googleapis.com/maps/api/directions/json"

    # APIリクエストのパラメータを構築
    params = {
        "origin": origin,
        "destination": destination,
        "waypoints": "|".join(waypoints) if waypoints else None,  # 経由地をパイプで連結
        "mode": "driving",
        "departure_time": departure_time,
        "optimizeWaypoints": "true",
        "key": api_key,
    }

    # クエリパラメータをURLエンコード
    query_string = urlencode({k: v for k, v in params.items() if v is not None})

    # 完全なURLを構築
    url = f"{base_url}?{query_string}"

    # APIリクエストを送信
    response = requests.get(url)

    # ステータスコードをチェック
    if response.status_code != 200:
        raise Exception(
            f"Google Maps API request failed with status code {response.status_code}: {response.text}"
        )
    print(url)
    # print(response.json())
    # 結果をJSONで返す
    return response.json()


# def generate_signed_url(bucket_name, object_name, expiration=3600):
#     """
#     署名付きURLを生成
#     """
#     storage_client = storage.Client()
#     bucket = storage_client.bucket(bucket_name)
#     blob = bucket.blob(object_name)

#     signed_url = blob.generate_signed_url(expiration=expiration)

#     return signed_url


# 緯度と経度を抽出
# def extract_lat_lng(data):
#     lat_lng_list = []

#     for route in data:
#         for leg in route["legs"]:
#             # legのstart_locationとend_locationを追加
#             lat_lng_list.append(
#                 {
#                     "type": "start_location",
#                     "lat": leg["start_location"]["lat"],
#                     "lng": leg["start_location"]["lng"],
#                 }
#             )
#             lat_lng_list.append(
#                 {
#                     "type": "end_location",
#                     "lat": leg["end_location"]["lat"],
#                     "lng": leg["end_location"]["lng"],
#                 }
#             )
#             # steps内のstart_locationとend_locationを追加
#             for step in leg["steps"]:
#                 lat_lng_list.append(
#                     {
#                         "type": "step_start_location",
#                         "lat": step["start_location"]["lat"],
#                         "lng": step["start_location"]["lng"],
#                     }
#                 )
#                 lat_lng_list.append(
#                     {
#                         "type": "step_end_location",
#                         "lat": step["end_location"]["lat"],
#                         "lng": step["end_location"]["lng"],
#                     }
#                 )
#     return lat_lng_list


def extract_lat_lng(data):
    """
    Google Maps Directions API のレスポンスから緯度経度を抽出する関数。
    """
    lat_lng_list = []

    # routes を処理
    for route in data.get("routes", []):
        # legs を処理
        for leg in route.get("legs", []):
            # leg の start_location と end_location を追加
            lat_lng_list.append(
                {
                    "type": "start_location",
                    "lat": leg["start_location"]["lat"],
                    "lng": leg["start_location"]["lng"],
                }
            )
            lat_lng_list.append(
                {
                    "type": "end_location",
                    "lat": leg["end_location"]["lat"],
                    "lng": leg["end_location"]["lng"],
                }
            )

            # steps を処理
            for step in leg.get("steps", []):
                # step の start_location と end_location を追加
                lat_lng_list.append(
                    {
                        "type": "step_start_location",
                        "lat": step["start_location"]["lat"],
                        "lng": step["start_location"]["lng"],
                    }
                )
                lat_lng_list.append(
                    {
                        "type": "step_end_location",
                        "lat": step["end_location"]["lat"],
                        "lng": step["end_location"]["lng"],
                    }
                )

    return lat_lng_list


def get_nearest_station(lat, lng):
    """
    指定した緯度経度から最寄り駅を取得する
    """
    try:
        # 最寄り駅を検索
        places_result = gmaps.places_nearby(
            location=(lat, lng),
            radius=5000,  # 半径2km以内を検索
            type="train_station",  # 駅を指定
        )

        if places_result.get("results"):
            # 最初の結果を最寄り駅とする
            nearest_station = places_result["results"][0]
            return {
                "name": nearest_station.get("name", "不明な駅"),
                "location": nearest_station.get("geometry", {}).get("location", {}),
            }
        else:
            raise HTTPException(
                status_code=404, detail="最寄り駅が見つかりませんでした。"
            )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error fetching nearest station: {str(e)}"
        )


# 条件を満たすお店を選択
def pick_stores(stores, store_list):
    """
    条件を満たすお店を選択し、picked_stores_listに情報を格納
    stores: [(お店の名前, カテゴリ番号), ...]
    store_list: お店の詳細情報リスト
    """
    # カテゴリ1のお店を抽出
    category_1_stores = [store for store in stores if store[1] == "1"]

    picked_stores = []
    picked_stores_list = []
    used_categories = set()
    used_names = set()

    # カテゴリ1のお店を1つ追加
    if category_1_stores:
        store = random.choice(category_1_stores)
        picked_stores.append(store[0])  # 名前を追加
        store_index = stores.index(store)
        picked_stores_list.append(
            store_list[store_index]
        )  # store_listから詳細情報を追加
        used_categories.add(store[1])  # カテゴリを記録
        used_names.add(store[0])  # 名前を記録

    # 残りの3つを選択
    for i, store in enumerate(stores):
        if len(picked_stores) == 4:  # 4つ選択完了したら終了
            break
        if store[1] not in used_categories and store[0] not in used_names:
            picked_stores.append(store[0])  # 名前を追加
            picked_stores_list.append(store_list[i])  # store_listから詳細情報を追加
            used_categories.add(store[1])  # カテゴリを記録
            used_names.add(store[0])  # 名前を記録

    return picked_stores, picked_stores_list


@app.post("/generate_response")
async def generate_response(prompt: str, thread_id: str = Query(default="default")):
    """
    ユーザーからのプロンプトに対して、GPT-4を用いて回答を生成し、過去の対話履歴を保持
    """
    try:
        # スレッドIDに基づいて履歴を取得
        current_history = thread_histories[thread_id]

        # 現在の履歴に新しいユーザープロンプトを追加
        messages = [
            {
                "role": "system",
                "content": """
#設定
あなたは旅行先を提案するアシスタントです。
入力された雰囲気から、まず旅行先の日本の地域（都道府県）を決定し、そこの商業施設の名称を挙げてください。
名称についてはGoogleマップで検索して出てくるものにしてください。
各商業施設はなるべく近くのものを選んでください。
商業施設の名称を決められない場合は、response_messageに深掘りする質問を記入してください。

#json出力
{"result":{
"region":"<region>",
"name":["<name>","<name>","<name>",],
"response_message":"<response_message>"}
""",
            }
        ]
        messages.extend(current_history)
        messages.append({"role": "user", "content": prompt})

        # GPT-4 APIを呼び出して応答を生成
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
        )

        # 応答内容を取得
        gpt_reply = response.choices[0].message.content
        # print(gpt_reply)

        # 対話履歴を更新
        thread_histories[thread_id].append({"role": "user", "content": prompt})
        thread_histories[thread_id].append({"role": "assistant", "content": gpt_reply})

        # 応答をJSONとしてパース
        suggestion = json.loads(gpt_reply)
        location_names = suggestion["result"]["name"]
        print(location_names)
        # print(suggestion["result"]["response_message"])
        response_message = suggestion["result"]["response_message"]

        # 各location_nameの座標を取得
        locations = []
        try:
            for name in location_names:
                # Google Places APIで場所の詳細情報を取得
                place_results = gmaps.find_place(
                    input=name,
                    input_type="textquery",
                    fields=["geometry", "formatted_address", "photos"],
                )
                if place_results.get("candidates"):
                    location_data = place_results["candidates"][0]

                    # 写真のリファレンスを取得
                    photo_reference = None
                    photos = location_data.get("photos", [])
                    if photos:
                        photo_reference = photos[0].get("photo_reference")

                    # # 写真のURLを生成
                    photo_url = (
                        f"https://maps.googleapis.com/maps/api/place/photo"
                        f"?maxwidth=400&photoreference={photo_reference}&key={GOOGLE_MAPS_API_KEY}"
                        if photo_reference
                        else None
                    )

                    # 署名付きURLを生成
                    # photo_url = None
                    # if photo_reference:
                    #     # ここで署名付きURLを生成（Google Cloud Storageを利用）
                    #     bucket_name = "your-google-cloud-bucket-name"  # バケット名
                    #     object_name = f"photos/{photo_reference}"  # オブジェクト名
                    #     # 署名付きURLを生成
                    #     photo_url = generate_signed_url(bucket_name, object_name)

                    # `locations`に情報を追加
                    locations.append(
                        {
                            "name": name,
                            "address": location_data.get(
                                "formatted_address", "住所不明"
                            ),
                            "location": location_data.get("geometry", {}).get(
                                "location", {}
                            ),
                            "photo": photo_url,
                        }
                    )
                else:
                    # 場所が見つからなかった場合のデフォルト値
                    locations.append(
                        {
                            "name": name,
                            "address": "住所不明",
                            "location": {},
                            "photo": None,
                        }
                    )

            # Google Maps Directions APIを使用してルート計算
            if len(location_names) < 2:
                raise HTTPException(
                    status_code=400,
                    detail="At least two locations are required for routing.",
                )
            # 出発地の最寄り駅を取得
            nearest_station = get_nearest_station(
                locations[0]["location"]["lat"], locations[0]["location"]["lng"]
            )
            origin = nearest_station["name"]
            destination = nearest_station["name"]  # ゴールも同じ駅
            print("出発地: ", nearest_station["name"])

            departure_time = datetime.now()
            # directions_result = gmaps.directions(
            #     origin=origin,  # 出発地
            #     destination=destination,  # 最終目的地
            #     waypoints=location_names,  # 経由地
            #     mode="driving",
            #     departure_time=departure_time,
            #     optimize_waypoints=True,
            # )

            directions_result = get_directions_api_response(
                api_key=GOOGLE_MAPS_API_KEY,
                origin=origin,
                destination=destination,
                waypoints=location_names,
                departure_time="now",
            )

            # directions_result = json.loads(
            #     get_directions_api_response(
            #         api_key=GOOGLE_MAPS_API_KEY,
            #         origin=location_names[0],
            #         destination=location_names[-1],
            #         waypoints=location_names[1:-1],
            #         departure_time="now",
            #     )
            # )
            # print(directions_result)
            """
            Google Places APIを使用して、行先候補周辺のECサイトを持つお店を取得
            """
            lat_lng_list = extract_lat_lng(directions_result)
            # for item in lat_lng_list:
            #     print(item)
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Error fetching nearby location: {str(e)}"
            )
        stores = []
        print("extract_lat_lng済")
        try:
            for item in lat_lng_list[::3]:
                location = (item["lat"], item["lng"])  # location=(latitude, longitude)
                print(f"Searching nearby stores for location: {location}")

                # Google Places APIを使って周辺の店舗を検索
                places_result = gmaps.places_nearby(
                    location=location,
                    radius=100,
                    type="store",  # 店舗タイプを指定
                )

                # ECサイトを持つ店舗をフィルタリング
                stores_with_websites = []
                try:
                    for place in places_result.get("results", []):
                        place_details = gmaps.place(place_id=place["place_id"])
                        website = place_details.get("result", {}).get("website")

                        # お店の画像URLを取得
                        photo_reference = None
                        photos = place_details.get("result", {}).get("photos", [])
                        if photos:
                            photo_reference = photos[0].get("photo_reference")

                        # 画像URLを構築
                        photo_url = (
                            f"https://maps.googleapis.com/maps/api/place/photo"
                            f"?maxwidth=400&photoreference={photo_reference}&key={GOOGLE_MAPS_API_KEY}"
                            if photo_reference
                            else None
                        )

                        if website:
                            if "convenience_store" not in place_details["result"].get(
                                "types", "不明"
                            ):

                                stores_with_websites.append(
                                    {
                                        "name": place_details["result"].get(
                                            "name", "不明な店舗"
                                        ),
                                        "website": website,
                                        "address": place_details["result"].get(
                                            "formatted_address", "住所不明"
                                        ),
                                        "rating": place_details["result"].get(
                                            "rating", "評価なし"
                                        ),
                                        "location": place_details["result"]
                                        .get("geometry", {})
                                        .get("location", {}),
                                        "photo": photo_url,
                                        "types": place_details["result"].get(
                                            "types", "不明"
                                        ),
                                    }
                                )
                    ###
                    # ECサイトのカテゴライズをstructure defineで生成AIによりfood、playingなどにカテゴライズして返却する
                    # 画像はBase64変換
                    ##
                except:
                    pass

                # 結果を追加
                stores.append({"location": location, "stores": stores_with_websites})
            # print(stores)
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Error fetching nearby stores: {str(e)}"
            )

        try:
            # お店の名前を抽出してリストに格納する
            store_names = []
            store_list = []
            # for store_group in stores:
            #     if "stores" in store_group:
            #         for store in store_group["stores"]:
            #             store_names.append(store["name"])
            for store_group in stores:
                print(store_group)
                for store in store_group["stores"]:
                    store_list.append(store)
                    store_names.append(store["name"])

            # 結果を表示
            print(store_names)
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                response_format={"type": "json_object"},
                messages=[
                    {
                        "role": "system",
                        "content": """
        #設定
        入力された店名に対し、以下の法則で順番ごとにカテゴリの番号を付けてください。番号は最も適したものを一つつけてください。

        Japanese sweets shop: 1
        Food Shops: 2
        Souvenir Shops: 3
        Dining & Drinking: 4
        Activity Shops: 5
        Other Retail Shops: 6

        #入力
        [<店名>,<店名>,<店名>]

        #json 出力
        {"result":["<num>","<num>","<num>",]}
        """,
                    },
                    {"role": "user", "content": str(store_names)},
                ],
            )
            categories = json.loads(response.choices[0].message.content)
            print(categories)
            additional_way_point = []
            # お店の情報をペアとして作成
            stores = list(zip(store_names, categories["result"]))

            # ピックアップ実行
            selected_stores, store_list = pick_stores(stores, store_list)
            print(selected_stores)
            visit_location = location_names + selected_stores

        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Error fetching nearby select_stores: {str(e)}"
            )

        try:
            print(location_names + selected_stores)
            directions_result = get_directions_api_response(
                api_key=GOOGLE_MAPS_API_KEY,
                origin=origin,
                destination=destination,
                waypoints=visit_location,
                departure_time="now",
            )
            print(directions_result)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error fetching nearby final_directions_result: {str(e)}",
            )

        return {
            "response_message": response_message,
            "route": directions_result,
            "location_names": locations,
            "stores": store_list,
            "waypoints": visit_location,
            "station": nearest_station,
        }

    except json.JSONDecodeError:
        raise HTTPException(
            status_code=400, detail="Invalid JSON format in GPT response."
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error processing request: {str(e)}"
        )

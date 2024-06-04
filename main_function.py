import requests, json

from flask import url_for
from functools import lru_cache

import os
from dotenv import load_dotenv

#몇번 요청했는지 기록. riot api 1초에 20번 요청 가능함
api_request_count = 0

def increment_api_count():
    global api_request_count
    api_request_count += 1

def get_api_request_count():
    return api_request_count

def cnt_reset():
    global api_request_count
    api_request_count = 0

@lru_cache(maxsize=10000)
def api_get_puuid( gameName=None, tagLine=None, region='asia'):
    """riot_id 및 riot_tag에서 puuid를 가져오기.

    Args:
        gameName (str, optional): Riot ID. Defaults == None.
        tagLine (str, optional): Riot Tag. Defaults == None.
        region (str, optional): Region. Defaults == 'asia'.

    Returns:
        puuid (str) : Player Universal Unique IDentifier
    """

    root_url = f'https://{region}.api.riotgames.com/'
    endpoint = f'riot/account/v1/accounts/by-riot-id/{gameName}/{tagLine}'

    response = requests.get(root_url+endpoint+'?'+'api_key='+api_key)
    increment_api_count()

    if "status" in response.json():
        print('api_get_puuid -' + str(response.json()))
        return 0
    
    # puuid = response.json()['puuid']

    return response.json()

@lru_cache(maxsize=10000)
def get_summoner_account_data( puuid=None, region='kr'):
    """puuid로 사용자의 계정정보 받아오기.

    Args:
        puuid (str, optional): Player Universal Unique IDentifier. Defaults == None.
        region (str, optional): Region. Defaults == 'kr'.

    Returns:
        id (str) : 암호화된 소환사 ID. 최대 63자.
        accountId (str) : 암호화된 계정 ID. 최대 56자.
        puuid (str) : 암호화된 PUUID. 총 78자.
        profileIconId (int) : 소환사와 연관된 소환사 아이콘의 ID.
        revisionDate (long) : 소환사 이름 변경, 소환사 레벨 변경 또는 프로필 아이콘 변경과 같은 이벤트가 이 타임스탬프를 업데이트.
        summonerLevel (long) :	소환사 레벨
    """

    root_url = f'https://{region}.api.riotgames.com/'
    endpoint = f'lol/summoner/v4/summoners/by-puuid/{puuid}'

    response = requests.get(root_url+endpoint+'?'+'api_key='+api_key)
    increment_api_count()

    if "status" in response.json():
        print('get_summoner_account_data -' + str(response.json()))
        return 0

    return response.json()

@lru_cache(maxsize=10000)
def get_summoner_game_data( id=None, region='kr'):
    """소환사 id로 소환사의 게임내 정보들 받아오기. 랭크가 없다면 값이 없는 리스트 반환함.

    Args:
        id (str, optional): 암호화된 소환사 id. Defaults == None.
        region (str, optional): Region. Defaults == 'kr'.

    Returns:
        leagueId (string)
        queueType (string) ?
        tier (string) : 소환사의 현재 티어.
        rank (string) : 소환사의 현재 랭크.
        summonerId (string) : 암호화된 소환사 id (파라미터값이랑 동일)
        leaguePoints (int) : 리그 포인트(LP)
        wins (int) : 승리한 횟수
        losses (int) : 패배한 횟수
        veteran	(boolean)	?
        inactive (boolean)	?
        freshBlood (boolean) ?
        hotStreak (boolean)	 ?
    """

    root_url = f'https://{region}.api.riotgames.com/'
    endpoint = f'lol/league/v4/entries/by-summoner/{id}'

    response = requests.get(root_url+endpoint+'?'+'api_key='+api_key)
    increment_api_count()

    if "status" in response.json():
        print('get_summoner_game_data -' + str(response.json()))
        return 0

    # target_queueType = "RANKED_SOLO_5x5"
    index = None

    #get_summoner_game_data queutype이 여러개라서 수정했음
    for i, participant in enumerate(response.json()):
        if participant["queueType"] == "RANKED_SOLO_5x5":
            index = i
            break

    if index == None:
        return response.json()

    return response.json()[i]

def get_summoner_matchId( puuid=None, start=0, count=20, region='asia'):
    """puuid로 사용자의 matchId들 받아오기

    Args:
        puuid (str, optional): puuid. Defaults == None.
        start (int, optional): 시작 인덱스번호. Defaults == 0.
        count (int, optional): 반환할 matchId의 개수. (0-100) Defaults == 20.
        region (str, optional): Region. Defaults == 'asia'.

    Returns:
        matchId (str) : 사용자가 플레이했던 매치들의 Id들
    """

    root_url = f'https://{region}.api.riotgames.com/'
    endpoint = f'lol/match/v5/matches/by-puuid/{puuid}/'

    response = requests.get(f'{root_url}{endpoint}ids?start={start}&count={count}&api_key={api_key}')
    increment_api_count()

    if "status" in response.json():
        print('get_summoner_matchId -' + str(response.json()))
        return 0

    return response.json()

@lru_cache(maxsize=10000)
def get_matches_data( matchId=None, puuid=None, region='asia'):
    """matchId 및 gameName에서 해당 매치에서의 사용자 정보를 가져오기.

    Args:
        matchId (int, optional): 조회하고싶은 판의 매치아이디. Defaults == None.
        gameName (str, optional): Riot ID. Defaults == None.
        region (str, optional): Region. Defaults == 'asia'.

    Returns:

    """

    root_url = f'https://{region}.api.riotgames.com/'
    endpoint = f'lol/match/v5/matches/{matchId}'

    response = requests.get(root_url+endpoint+'?'+'api_key='+api_key)
    increment_api_count()

    queues_dict = get_queues_dict()

    if "status" in response.json():
        print('get_matches_data -' + str(response.json()))
        return 0

    gameMode = response.json()["info"]["gameMode"]
    queueId = queues_dict[str(response.json()['info']["queueId"])].replace('5v5 ', "").replace(' games', "").replace(" (Quickplay)", "")

    #아레나 모드는 아직 아이콘파일이 없어서 제외함
    if gameMode == 'CHERRY':
        return 0, 0

    index = None
    originalGameName = ''
    for i, participant in enumerate(response.json()['info']['participants']):
        # if participant['riotIdGameName'].lower() == gameName.lower():
        if participant['puuid'] == puuid:
            index = i
            break

    return response.json()['info']['participants'][index], queueId

def win_rate20( puuid=None ):
    """puuid에서 사용자의 최근 20판 승률계산.

    Args:
        puuid (str, optional): Player Universal Unique IDentifier. Defaults == None.
    Returns:
        winRate (int) : 사용자의 최근 20판 승률.
        win (int) : 사용자의 최근 20판중 승리한 판수.
        lose (int) : 사용자의 최근 20판중 패배한 판수.
    """

    matchIds = get_summoner_matchId( puuid, count=20)
    if len(matchIds) == 0:
        return [0,0,0]

    win = 0
    lose = 0

    for i in range(20):
        matchData, gameMode = get_matches_data(matchIds[i], puuid)
        if matchData == 0:
            continue
        if matchData['win'] == True:
            win += 1
        else:
            lose += 1

    winRate = win/(win+lose)*100

    wins = [winRate, win, lose]

    return wins

@lru_cache(maxsize=10000)
def spectator( puuid=None, region='kr'):
    """puuid에서 현재 진행중인 게임 정보를 가져오기.

    Args:
        puuid (str, optional): Player Universal Unique IDentifier. Defaults == None.

    Returns:

    """

    root_url = f'https://{region}.api.riotgames.com/'
    endpoint = f'lol/spectator/v5/active-games/by-summoner/{puuid}'

    response = requests.get(root_url+endpoint+'?'+'api_key='+api_key)
    increment_api_count()

    #오류 코드 분기점
    if "status" in response.json():
        if response.json()['status']['message'] == "Data not found - spectator game info isn't found":
            return 'Offline'
        else:
            print('spectator -' + str(response.json()))
            return 0
    else:
        return 'Online'

@lru_cache(maxsize=10000)
def get_mastery( puuid=None, count=3,  region='kr'):
    """puuid에서 사용자의 캐릭터 숙련도를 가져오기.

    Args:
        puuid (str, optional): Player Universal Unique IDentifier. Defaults == None.
        count (int, optional): 불러오고싶은 데이터 수의 양. 가장 높은것부터 차례대로 반환. Defaults == 3.
        region (str, optional): Region. Defaults == 'kr'.

    Returns:
        puuid (str) : Player Universal Unique IDentifier
    """

    root_url = f'https://{region}.api.riotgames.com/'
    endpoint = f'lol/champion-mastery/v4/champion-masteries/by-puuid/{puuid}/top?count={count}&'

    response = requests.get(root_url+endpoint+'api_key='+api_key)
    increment_api_count()

    if "status" in response.json():
        print('get_mastery -' + str(response.json()))
        return 0

    mastery = [
    ]

    champ_dict = get_champ_dict()

    for i in range(3):
        if response.json()[i]['championLevel'] >= 10:
            masteryLevel = 10
        else:
            masteryLevel = response.json()[i]['championLevel']

        mastery.append({'championName':champ_dict[response.json()[i]['championId']],
                        'championPoints':format(response.json()[i]['championPoints'], ','),
                        'champIcon': f"https://ddragon.leagueoflegends.com/cdn/14.10.1/img/champion/{champ_dict[response.json()[i]['championId']]}.png",
                        'masteryIcon':f'/static/images/mastery/Mastery_Level_{masteryLevel}_Crest.png'})

    return mastery

@lru_cache(maxsize=10000)
def ddragon_get_spell_dict(version="14.10.1"):
    url = f"https://ddragon.leagueoflegends.com/cdn/{version}/data/en_US/summoner.json"
    html = requests.get(url).json()

    spell_dict = {}

    # data 내의 모든 key와 id 값을 추출하여 새로운 구조에 저장합니다.
    for key, value in html['data'].items():
        id_value = int(value['key'])  # 'key' 값을 id_value로 저장
        spell_dict[id_value] = key  # id_value를 키로, key를 값으로 저장

    return spell_dict

@lru_cache(maxsize=10000)
def ddragon_get_runes_dict(version="14.10.1"):
    url = f"http://ddragon.leagueoflegends.com/cdn/{version}/data/en_US/runesReforged.json"
    html = requests.get(url).json()
    rune_dict = {rune["id"]: rune["key"] for item in html for slot in item["slots"] for rune in slot["runes"]}
    perk_dict = {item["id"]: item["key"] for item in html}
    perk_img_dict = {8100:7200, 8000:7201, 8200:7202, 8300:7203, 8400:7204}

    #여진 이름이 사전이랑 달라서 수정.
    rune_dict[8439] = 'VeteranAftershock'
    rune_dict[8008] = 'LethalTempoTemp'

    return perk_dict , rune_dict, perk_img_dict

@lru_cache(maxsize=10000)
def get_champ_dict(version="14.10.1"):
    url = f"https://ddragon.leagueoflegends.com/cdn/{version}/data/en_US/champion.json"
    response = requests.get(url).json()["data"]

    champId_dict= {

    }
    for champion_data in response.values():
        champion_key = int(champion_data["key"])
        champion_name = champion_data["id"]
        champId_dict[champion_key] = champion_name

    return champId_dict

def get_queues_dict():

    current_directory = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_directory, 'queues_dict.json')
    with open(file_path, 'r') as file:
        loaded_game_modes = json.load(file)

    return loaded_game_modes

def matchdata_parsing(matchId=None, puuid=None):

    matchData, gameMode = get_matches_data(matchId, puuid)
    if matchData == 0:
        return 0

    #스펠이랑 룬 ID값으로 이름 찾아오기
    spell_dict = ddragon_get_spell_dict()
    perk_dict , rune_dict , perk_img_dict = ddragon_get_runes_dict()

    #룬 Key값들 파싱
    rune1Main = matchData["perks"]["styles"][0]["style"]
    rune1Sub = matchData["perks"]["styles"][0]["selections"][0]["perk"]
    rune2Main = matchData["perks"]["styles"][1]["style"]

    #게임시간 (ms -> m 변환)
    gameLength = int(matchData["challenges"]["gameLength"])//60

    #승패 여부
    if matchData["win"] == True and gameLength < 3:
        win = "Remake"
    elif matchData["win"] == True:
        win = "win"
    else:
        win = "Lose"



    #룬 아이콘 링크가 옛날버전이라 영감이 없음.
    if perk_dict[rune2Main] == "Inspiration":
        rune2 = 'Whimsy'
    else:
        rune2 = perk_dict[rune2Main]

    #아이템이 있는경우 아이템이미지링크, 없으면 빈 네모. (아이템이 없으면 id가 0)
    itemIcons = []
    for i in range(7):
        n = f'item{i}'
        if matchData[n] == 0:
            itemIcons.append(url_for('static', filename='images/itemEmpty.png'))
            # itemIcons.append('test')
        else:
            itemIcons.append(f"https://ddragon.leagueoflegends.com/cdn/14.10.1/img/item/{matchData[n]}.png")

    #멀티킬 데이터 정리
    if matchData["pentaKills"] > 0:
        multiKills = "Penta Kills"
    elif matchData["quadraKills"] > 0:
        multiKills = "Quadra Kills"
    elif matchData["tripleKills"] > 0:
        multiKills = "Triple Kills"
    elif matchData["doubleKills"] > 0:
        multiKills = "Double Kills"
    else:
        multiKills = ' '

    matches = {
        "gameMode": gameMode,
        "win": win,
        "championId": matchData["championId"],
        "championName": matchData["championName"],
        "gameLength": gameLength,
        'kills': matchData['kills'],
        "deaths": matchData["deaths"],
        'assists': matchData['assists'],
        "kda": round(matchData["challenges"]["kda"], 2),
        'multiKills': multiKills,
        "cs": matchData["totalMinionsKilled"] + matchData["totalAllyJungleMinionsKilled"] + matchData['totalEnemyJungleMinionsKilled'],
        'csPerMin': round((matchData["totalMinionsKilled"] + matchData["totalAllyJungleMinionsKilled"] + matchData['totalEnemyJungleMinionsKilled']) / gameLength, 1),
        "rune1": matchData["perks"]["styles"][0]["selections"][0]["perk"],
        "rune2": matchData["perks"]["styles"][1]["style"],

        "champIcon": f"https://ddragon.leagueoflegends.com/cdn/14.10.1/img/champion/{matchData['championName']}.png",
        "item0Icon": itemIcons[0],
        "item1Icon": itemIcons[1],
        "item2Icon": itemIcons[2],
        "item3Icon": itemIcons[3],
        "item4Icon": itemIcons[4],
        "item5Icon": itemIcons[5],
        "item6Icon": itemIcons[6],
        "spell1Icon": f"https://ddragon.leagueoflegends.com/cdn/14.10.1/img/spell/{spell_dict[matchData['summoner1Id']]}.png",
        "spell2Icon": f"https://ddragon.leagueoflegends.com/cdn/14.10.1/img/spell/{spell_dict[matchData['summoner2Id']]}.png",
        "rune1Icon": f"https://ddragon.leagueoflegends.com/cdn/img/perk-images/Styles/{perk_dict[rune1Main]}/{rune_dict[rune1Sub]}/{rune_dict[rune1Sub]}.png",
        "rune2Icon": f"https://ddragon.leagueoflegends.com/cdn/img/perk-images/Styles/{perk_img_dict[rune2Main]}_{rune2}.png"
    }

    #치속 이미지를 ddragon.leagueoflegends에서 제공안함
    if matches['rune1Icon'] == 'https://ddragon.leagueoflegends.com/cdn/img/perk-images/Styles/Precision/LethalTempoTemp/LethalTempoTemp.png':
        matches['rune1Icon'] = 'https://ddragon.canisback.com/img/perk-images/Styles/Precision/LethalTempo/LethalTempoTemp.png'

    return matches
#"10.6.1"
def champdata_analyze(matches):
    champdata = []
    for match in matches:
        win_value = 1 if match['win'] == 'win' else 0
        lose_value = 1 if match['win'] == 'Lose' else 0
        data = {
            'win': win_value,
            'lose': lose_value,
            'championId': match['championId'],
            'championName': match['championName'],
            'kills': match['kills'],
            'deaths': match['deaths'],
            'assists': match['assists'],
            'cs': match['cs']
        }
        champdata.append(data)

    return champdata

def aggregate_champion_data(extracted_data, champ_dict):
    champion_ids = list(set([data['championId'] for data in extracted_data]))  # 중복 제거된 championId 리스트
    aggregated_data = {}

    for champion_id in champion_ids:
        if len(champ_dict[champion_id]) > 7:
            championName = champ_dict[champion_id][:7] + '..'
        else:
            championName = champ_dict[champion_id]

        aggregated_data[champion_id] = {
            'championId': champion_id,
            'championName': championName,
            'championIcon': f'https://ddragon.leagueoflegends.com/cdn/14.10.1/img/champion/{champ_dict[champion_id]}.png',
            'total_wins': 0,
            'total_loses': 0,
            'total_kills': 0,
            'total_deaths': 0,
            'total_assists': 0,
            'total_cs': 0
        }

    for data in extracted_data:
        champion_id = data['championId']
        win = data['win']
        lose = data['lose']
        kills = data['kills']
        deaths = data['deaths']
        assists = data['assists']
        cs = data['cs']

        aggregated_data[champion_id]['total_wins'] += win
        aggregated_data[champion_id]['total_loses'] += lose
        aggregated_data[champion_id]['total_kills'] += kills
        aggregated_data[champion_id]['total_deaths'] += deaths
        aggregated_data[champion_id]['total_assists'] += assists
        aggregated_data[champion_id]['total_cs'] += cs

    #정렬 기준에 판수 말고 승률도 포함시킴
    sorted_data = sorted(aggregated_data.values(), key=lambda x: (total_games(x), x['total_wins']), reverse=True)
    top_5 = sorted_data[:5]

    for data in top_5:
        matches = data['total_wins'] + data['total_loses']
        data['winRate'] = round(data['total_wins']/matches*100)
        data['total_kills'] = round(data['total_kills']/matches, 1)
        data['total_deaths'] = round(data['total_deaths']/matches, 1)
        data['total_assists'] = round(data['total_assists']/matches, 1)

        #ZeroDivisionError
        if data['total_deaths'] != 0:
            data['kda'] = round((data['total_kills'] + data['total_assists']) / data['total_deaths'], 2)
        else:
            data['kda'] = round((data['total_kills'] + data['total_assists']) , 2)


    return top_5

def total_games(data):
    total_wins = data['total_wins']
    total_loses = data['total_loses']
    total_games = total_wins + total_loses
    return total_games

#프로필 갱신하기
def claim_profile():
    # 캐싱된 데이터들 삭제
    get_summoner_account_data.cache_clear()
    get_summoner_game_data.cache_clear()
    spectator.cache_clear()
    get_mastery.cache_clear()

# Usage
# project_folder = os.path.expanduser('~/mysite')  # adjust as appropriate
# load_dotenv(os.path.join(project_folder, '.env'))
load_dotenv()
api_key = os.getenv("RIOT_API_KEY")  # 환경 변수에서 API 키를 가져옴
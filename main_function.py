import requests

from flask import url_for

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
    puuid = response.json()['puuid']
    return puuid

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

    return response.json()

def get_summoner_game_data( id=None, region='kr'):
    """소환사 id로 소환사의 게임내 정보들 받아오기.

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

    return response.json()

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

    return response.json()

def get_matches_data( matchId=None, gameName=None, region='asia'):
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

    gameMode = response.json()["info"]["gameMode"]

    target_game_name = gameName
    index = None

    for i, participant in enumerate(response.json()['info']['participants']):
        if participant['riotIdGameName'] == target_game_name:
            index = i
            break

    return response.json()['info']['participants'][index], gameMode

def win_rate20( puuid=None, gameName=None):
    """puuid에서 사용자의 최근 20판 승률계산.

    Args:
        puuid (str, optional): Player Universal Unique IDentifier. Defaults == None.
    Returns:
        winRate (int) : 사용자의 최근 20판 승률.
        win (int) : 사용자의 최근 20판중 승리한 판수.
        lose (int) : 사용자의 최근 20판중 패배한 판수.
    """
    matchIds = get_summoner_matchId( puuid, count=20)
    win = 0
    
    for i in range(20):
        matchData, gameMode = get_matches_data(matchIds[i], gameName)
        if matchData['win'] == True:
            win += 1

    winRate = win/20*100
    lose = 20-win

    wins = [winRate, win, lose]

    return wins

def spectator( puuid=None, region='kr'):
    """puuid에서 현재 진행중인 게임 정보를 가져오기.

    Args:
        puuid (str, optional): Player Universal Unique IDentifier. Defaults == None.

    Returns:
        
    """

    root_url = f'https://{region}.api.riotgames.com/'
    endpoint = f'lol/spectator/v5/active-games/by-summoner/{puuid}'

    response = requests.get(root_url+endpoint+'?'+'api_key='+api_key)

    return response.json()

def in_game( puuid=None):
    """puuid에서 현재 사용자가 게임중인지 아닌지 체크

    Args:
        puuid (str, optional): Player Universal Unique IDentifier. Defaults == None.

    Returns:
        state (int): 사용자가 게임중이라면 1, 아니면 0
    """

    if 'status' in spectator(puuid):
        state = 'Offline'
    else:
        state = 'Online'

    return state

def ddragon_get_spell_dict(version="14.10.1"):
    url = f"https://ddragon.leagueoflegends.com/cdn/{version}/data/en_US/summoner.json"
    html = requests.get(url).json()
    
    spell_dict = {}

    # data 내의 모든 key와 id 값을 추출하여 새로운 구조에 저장합니다.
    for key, value in html['data'].items():
        id_value = int(value['key'])  # 'key' 값을 id_value로 저장
        spell_dict[id_value] = key  # id_value를 키로, key를 값으로 저장

    return spell_dict

def ddragon_get_runes_dict(version="14.10.1"):
    url = f"http://ddragon.leagueoflegends.com/cdn/{version}/data/en_US/runesReforged.json"
    html = requests.get(url).json()
    rune_dict = {rune["id"]: rune["key"] for item in html for slot in item["slots"] for rune in slot["runes"]}
    perk_dict = {item["id"]: item["key"] for item in html}
    perk_img_dict = {8100:7200, 8000:7201, 8200:7202, 8300:7203, 8400:7204}

    return perk_dict , rune_dict, perk_img_dict

def matchdata_parsing(matchId=None, gameName=None):

    matchData, gameMode = get_matches_data(matchId, gameName)

    #스펠이랑 룬 ID값으로 이름 찾아오기
    spell_dict = ddragon_get_spell_dict()
    perk_dict , rune_dict , perk_img_dict = ddragon_get_runes_dict()

    #룬 Key값들 파싱
    rune1Main = matchData["perks"]["styles"][0]["style"]
    rune1Sub = matchData["perks"]["styles"][0]["selections"][0]["perk"]
    rune2Main = matchData["perks"]["styles"][1]["style"]

    #승패 여부
    if matchData["win"] == True:
        win = "win"
    else:
        win = "Lose"

    #게임시간 (ms -> m 변환)
    gameLength = int(matchData["challenges"]["gameLength"])//60

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
        else:
            itemIcons.append(f"https://ddragon.leagueoflegends.com/cdn/14.10.1/img/item/{matchData[n]}.png")

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
        "doubleKills": matchData["doubleKills"],
        "tripleKills": matchData["tripleKills"],
        "quadraKills": matchData["quadraKills"],
        "pentaKills": matchData["pentaKills"],
        "cs": matchData["totalMinionsKilled"],
        "rune1": matchData["perks"]["styles"][0]["selections"][0]["perk"],
        "rune2": matchData["perks"]["styles"][1]["style"],
        
        "champIcon": f"https://ddragon.leagueoflegends.com/cdn/14.10.1/img/champion/{matchData["championName"]}.png",
        "item0Icon": itemIcons[0],
        "item1Icon": itemIcons[1],
        "item2Icon": itemIcons[2],
        "item3Icon": itemIcons[3],
        "item4Icon": itemIcons[4],
        "item5Icon": itemIcons[5],
        "item6Icon": itemIcons[6],
        "spell1Icon": f"https://ddragon.leagueoflegends.com/cdn/14.10.1/img/spell/{spell_dict[matchData["summoner1Id"]]}.png",
        "spell2Icon": f"https://ddragon.leagueoflegends.com/cdn/14.10.1/img/spell/{spell_dict[matchData["summoner2Id"]]}.png",
        "rune1Icon": f"https://ddragon.leagueoflegends.com/cdn/img/perk-images/Styles/{perk_dict[rune1Main]}/{rune_dict[rune1Sub]}/{rune_dict[rune1Sub]}.png",
        "rune2Icon": f"https://ddragon.leagueoflegends.com/cdn/img/perk-images/Styles/{perk_img_dict[rune2Main]}_{rune2}.png"
    }
    return matches
#아이템이 없는 경우 구현"10.6.1"


# Usage
api_key = 'RGAPI-141ae431-067a-4a05-946d-2030aba68f18'
# gameName = '산타 질리언'
# tag_line = '1225'

# puuid = api_get_puuid(gameName, tag_line)
# account_data = get_summoner_account_data(puuid)
# id = account_data['id']

# print(puuid)

# a = get_matches_data('KR_7087492574', gameName)
# print(a)

# def matches_functions(gameName, tag_line):

#     matchHistory = [
#         # {'date': '2024-05-27', 'data': 'data1', 'result': 'Win'},
#         # {'date': '2024-05-26', 'data': 'data2', 'result': 'Lose'},
#         # 여기 매치 데이터 추가해야함.
#     ]

#     matchIds = get_summoner_matchId(api_get_puuid(gameName, tag_line))
#     for i in range(len(matchIds)):
#         matches = matchdata_parsing(matchIds[i], gameName)
#         matchHistory.append(matches)


#     return matchHistory

# a = matches_functions(gameName, tag_line)
# print(a[5])

# a = get_summoner_matchId(puuid)
# # a = get_matches_data('KR_7088339652', gameName)
# print(a)

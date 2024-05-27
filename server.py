from flask import Flask, request, render_template
from main_function import *

app = Flask(__name__)

def profile_functions():
    #입력값을 # 기준으로 쪼개기
    inputs = request.form['inputs'].split('#')

    #riot api로 데이터 불러오기
    puuid = api_get_puuid(inputs[0], inputs[1])
    accountData = get_summoner_account_data(puuid)
    summonerGameData = get_summoner_game_data(accountData['id'])
    winRate = win_rate20(puuid,inputs[0])

    if len(summonerGameData) == 1:
        tier = f'{summonerGameData[0]['tier']} {summonerGameData[0]['rank']} - {summonerGameData[0]['leaguePoints']}LP'
    else:
        tier = f'unranked'

    profileData = {
        'name': inputs[0],
        'level': accountData['summonerLevel'],
        'id': accountData['id'],
        'icon': f"https://ddragon.leagueoflegends.com/cdn/14.10.1/img/profileicon/{accountData['profileIconId']}.png",
        'tier': tier,
        'winRate': winRate[0],
        'win': winRate[1],
        'lose': winRate[2],
        'inGame': in_game(puuid)
    }

    return profileData

def matches_functions():
    inputs = request.form['inputs'].split('#')

    matchId = None

    matchData, gameMode = get_matches_data(matchId, inputs[0])
    styles = [style['style'] for style in matchData['styles']]

    matchHistory = {
        "gameMode": gameMode,
        "win": matchData["win"],
        "championId": matchData["championId"],
        "championName": matchData["championName"],
        "gameLength": matchData["gameLength"],
        'kills': matchData['kills'],
        "deaths": matchData["deaths"],
        'assists': matchData['assists'],
        "kda": matchData["kda"],
        "item0": matchData["item0"],
        "item1": matchData["item1"],
        "item2": matchData["item2"],
        "item3": matchData["item3"],
        "item4": matchData["item4"],
        "item5": matchData["item5"],
        "item6": matchData["item6"],
        "spellId1": matchData["summoner1Id"],
        "spellId2": matchData["summoner2Id"],
        "doubleKills": matchData["doubleKills"],
        "tripleKills": matchData["tripleKills"],
        "quadraKills": matchData["quadraKills"],
        "pentaKills": matchData["pentaKills"],
        "cs": matchData["totalMinionsKilled"],
        "rune1": styles[0],
        "rune2": styles[1]
    }

    return matchHistory

#매치데이터 수가 0인경우도 생각해야함

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('main.html')

@app.route('/profile/', methods=['POST'])
def profile():
    if request.method == 'POST':
        profileData = profile_functions()
        matchHistory = matches_functions()

        return render_template('profile.html', profileData=profileData)#, matchHistory=matchHistory)
    return 'wrong'

if __name__ == '__main__':
    app.run(debug=True)

#이름옆에 태그추가
#점수 숫자에 , 추가하기
#이름 검색 안되면 오류 말고 다른창 띄우기

# 매치데이터 필요한거
# 챔피언,게임모드, 킬, 데스, 어시 +(3변수로 평점계산), 스펧, 룬, 아이템, 승리여부. 시간, 몇분전인지.
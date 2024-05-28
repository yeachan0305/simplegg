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
        tier = 'unranked'

    tierImg = url_for('static', filename=f'images/rank/Rank={summonerGameData[0]['tier']}.png')

    profileData = {
        'name': inputs[0],
        'tagline': inputs[1],
        'level': accountData['summonerLevel'],
        'id': accountData['id'],
        'icon': f"https://ddragon.leagueoflegends.com/cdn/14.10.1/img/profileicon/{accountData['profileIconId']}.png",
        'tier': tier,
        'winRate': round(winRate[0], 1),
        'win': winRate[1],
        'lose': winRate[2],
        'inGame': in_game(puuid),
        'tierIcon': tierImg
    }
    return profileData

def matches_functions():
    inputs = request.form['inputs'].split('#')

    matchHistory = [
    ]

    matchIds = get_summoner_matchId(api_get_puuid(inputs[0], inputs[1]))
    for i in range(len(matchIds)):
        matches = matchdata_parsing(matchIds[i], inputs[0])
        matchHistory.append(matches)


    return matchHistory


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('main.html')

@app.route('/profile/', methods=['POST'])
def profile():
    if request.method == 'POST':
        profileData = profile_functions()
        matchHistory = matches_functions()

        return render_template('testt2 copy.html', profileData=profileData, matchHistory=matchHistory)
    return 'wrong'

if __name__ == '__main__':
    app.run(debug=True)

#이름 검색 안되면 오류 말고 다른창 띄우기
#솔랭, 일겜 구분
#여진 아이콘 안나옴, 랭크 아이콘 크기수정 (혹시 파일마다 크기가 다른가?)
#온라인 표시면 초록색으로 하기
#매치데이터 수가 0인경우도 생각해야함
#claim profile 버튼 구현

#챔프 숙련도 1개 뽑아오기 + 그걸로 메인 프로필이미지
# https://kr.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-puuid/
# riODzRw9cp8dMNr29Jle17t50eoRWkl72e48TzZ7IDec8sVAbiYoDjTHyUEFY2QBYHI2mRKsttO8eA/
# top?count=1&api_key=RGAPI-6e7e14a6-294b-4ff7-8e37-310b3154418e

#게임 타입
# https://static.developer.riotgames.com/docs/lol/queues.json

#랭킹
# https://kr.api.riotgames.com/lol/league-exp/v4/entries/RANKED_SOLO_5x5/CHALLENGER/I?page=1&api_key=RGAPI-6e7e14a6-294b-4ff7-8e37-310b3154418e
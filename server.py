from flask import Flask, request, render_template
from main_function import *

app = Flask(__name__)

def profile_functions(puuid):
    #입력값을 # 기준으로 쪼개기
    inputs = request.form['inputs'].split('#')

    #riot api로 데이터 불러오기
    accountData = get_summoner_account_data(puuid)

    summonerGameData = get_summoner_game_data(accountData['id'])
    winRate = win_rate20(puuid, inputs[0])

    #챔피언 숙련도 불러오기
    mastery = get_mastery(puuid)
    champ_dict = get_champ_dict()

    if len(summonerGameData) >= 1:
        tier = summonerGameData['tier']
    else:
        tier = 'UNRANKED'

    tierImg = url_for('static', filename=f'images/rank/Rank={tier}.png')

    profileData = {
        'name': inputs[0],
        'tagline': inputs[1],
        'level': accountData['summonerLevel'],
        'id': accountData['id'],
        'icon': f"https://ddragon.leagueoflegends.com/cdn/14.10.1/img/profileicon/{accountData['profileIconId']}.png",
        'tier': tier,
        'rank': 0,
        'lp': 0,
        'winRate': round(winRate[0], 1),
        'win': winRate[1],
        'lose': winRate[2],
        'inGame': spectator(puuid),
        'tierIcon': tierImg,

        'championId1':mastery['championId1'],
        'championId2':mastery['championId2'],
        'championId3':mastery['championId3'],
        'championLevel1':mastery['championLevel1'],
        'championLevel2':mastery['championLevel2'],
        'championLevel3':mastery['championLevel3'],
        'championPoints1':mastery['championPoints1'],
        'championPoints2':mastery['championPoints2'],
        'championPoints3':mastery['championPoints3'],
        'champbackground':f'https://ddragon.leagueoflegends.com/cdn/img/champion/splash/{champ_dict[mastery['championId1']]}_0.jpg'
    }

    if tier == 'UNRANKED':
        pass
    else:
        profileData['rank'] = summonerGameData['rank']
        profileData['lp'] = summonerGameData['leaguePoints']

    return profileData

def matches_functions(puuid):
    inputs = request.form['inputs'].split('#')

    matchHistory = [
    ]

    matchIds = get_summoner_matchId(puuid)
    for i in range(len(matchIds)):
        matches = matchdata_parsing(matchIds[i], inputs[0])
        matchHistory.append(matches)


    return matchHistory

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('main.html')

@app.route('/profile/', methods=['POST1','POST2'])
def profile():
    if request.method == 'POST1':
        inputs = request.form['inputs'].split('#')  
        #puuid 중복 요청을 그냥 메인에서 하나로 함.
        puuid = api_get_puuid(inputs[0], inputs[1])

        profileData = profile_functions(puuid)
        matchHistory = matches_functions(puuid)

        cnt = get_api_request_count()
        print(cnt)

        return render_template('profile v4.html', profileData=profileData, matchHistory=matchHistory)
    elif request.method == 'POST2':
        claim_profile()

        inputs = request.form['inputs'].split('#')  
        #puuid 중복 요청을 그냥 메인에서 하나로 함.
        puuid = api_get_puuid(inputs[0], inputs[1])

        profileData = profile_functions(puuid)
        matchHistory = matches_functions(puuid)

        cnt = get_api_request_count()
        print(cnt)
        return render_template('profile v4.html', profileData=profileData, matchHistory=matchHistory)

if __name__ == '__main__':
    app.run(debug=True)

#이름 검색 안되면 오류 말고 다른창 띄우기
#솔랭, 일겜 구분
#랭크 아이콘 크기수정 (이름 길이가 티어 이미지까지 오면 이미지가 아래로감   )(혹시 파일마다 크기가 다른가?) + 언랭크 아이콘 추가
#매치데이터 수가 0인경우도 생각해야함
#claim profile 버튼 구현


#게임 타입
# https://static.developer.riotgames.com/docs/lol/queues.json

#랭킹
# https://kr.api.riotgames.com/lol/league-exp/v4/entries/RANKED_SOLO_5x5/CHALLENGER/I?page=1&api_key=RGAPI-6e7e14a6-294b-4ff7-8e37-310b3154418e
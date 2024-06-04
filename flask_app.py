from flask import Flask, request, render_template, flash, redirect, url_for
from main_function import *
from dotenv import load_dotenv
import traceback, os

app = Flask(__name__)

# project_folder = os.path.expanduser('~/mysite')  # adjust as appropriate
# load_dotenv(os.path.join(project_folder, '.env'))
load_dotenv()
app.secret_key = os.getenv("SECRET_KEY")

def profile_functions(puuid):
    #입력값을 # 기준으로 쪼개기

    #riot api로 데이터 불러오기
    accountData = get_summoner_account_data(puuid['puuid'])
    summonerGameData = get_summoner_game_data(accountData['id'])
    winRate = win_rate20(puuid['puuid'])

    #챔피언 숙련도 불러오기
    mastery = get_mastery(puuid['puuid'])
    champ_dict = get_champ_dict()

    #랭크가 없는데, 배치고사만 본 경우 오류가 떠서 제외시킴.
    if len(summonerGameData) >= 1:
        if type(summonerGameData) == list:
            tier = 'UNRANKED'
        else:
            tier = summonerGameData['tier']
    else:
        tier = 'UNRANKED'

    tierImg = url_for('static', filename=f'images/rank/Rank={tier}.png')

    profileData = {
        'name': puuid['gameName'],
        'tagline': puuid['tagLine'],
        'level': accountData['summonerLevel'],
        'id': accountData['id'],
        'icon': f"https://ddragon.leagueoflegends.com/cdn/14.10.1/img/profileicon/{accountData['profileIconId']}.png",
        'tier': tier,
        'rank': '',
        'lp': 0,
        'winRate': round(winRate[0], 1),
        'win': winRate[1],
        'lose': winRate[2],
        'inGame': spectator(puuid['puuid']),
        'tierIcon': tierImg,
        'mastery': mastery,
        'champbackground':f"https://ddragon.leagueoflegends.com/cdn/img/champion/splash/{mastery[0]['championName']}_0.jpg"
    }

    #unraked는 rank랑 lp가 없음
    #첼린저, 그랜드마스터, 마스터는 rank만 없음.
    if tier == 'CHALLENGER' or tier == 'GRANDMASTER' or tier == 'MASTER':
        profileData['lp'] = format(summonerGameData['leaguePoints'], ',')
    elif tier == 'UNRANKED':
        pass
    else:
        profileData['rank'] = summonerGameData['rank']
        profileData['lp'] = format(summonerGameData['leaguePoints'], ',')


    return profileData

def matches_functions(puuid):
    champ_dict = get_champ_dict()

    matchHistory = [
    ]

    matchIds = get_summoner_matchId(puuid)
    for i in range(len(matchIds)):
        matches = matchdata_parsing(matchIds[i], puuid)
        if matches == 0:
            continue
        matchHistory.append(matches)

    winrateTop5Data = aggregate_champion_data(champdata_analyze(matchHistory), champ_dict)

    return matchHistory, winrateTop5Data

@app.route('/', methods=['GET', 'POST'])
def index():

    #페이지 불러올때 미리 캐싱해서 속도 개선
    a = get_champ_dict()
    # a = get_queues_dict()
    a,b,c = ddragon_get_runes_dict()
    a = ddragon_get_spell_dict()
    return render_template('main.html')

@app.route('/profile/', methods=['GET', 'POST'])
def profile():
    if request.method == 'POST':

        action = request.form['action']
        inputBuffer = request.form['inputs']
        inputs = request.form['inputs'].split('#')

        if action == 'POST2':
            claim_profile()

        cnt_reset()

        try:
            puuid = api_get_puuid(inputs[0], inputs[1])
            profileData = profile_functions(puuid)
        except Exception as ex:
            flash("해당 사용자를 찾을 수 없습니다.")
            err_msg = traceback.format_exc()
            print(err_msg)
            return redirect(url_for('index'))


        matchHistory, winrateTop5Data= matches_functions(puuid['puuid'])

        cnt = get_api_request_count()
        print(cnt)

        return render_template('profile.html', profileData=profileData, matchHistory=matchHistory,winrateTop5Data=winrateTop5Data, inputBuffer = inputBuffer)

if __name__ == '__main__':
    app.run(debug=True)
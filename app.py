
from flask import Flask, render_template, request
import os
import re
import openai
import requests
import math
from datetime import datetime
from dotenv import load_dotenv
from api_services import weather_service, kakao_service, krx_service, recipe_service, quote_service

# .env 파일에서 환경변수 로드
load_dotenv()

def get_kakao_directions_direct(departure, destination):
    """카카오 API를 직접 호출하여 교통 정보 제공"""
    
    # 환경변수에서 카카오 REST API 키 가져오기
    KAKAO_API_KEY = os.getenv('KAKAO_API_KEY')
    
    if not KAKAO_API_KEY:
        return "⚠️ 카카오 API 키가 설정되지 않았습니다.\n📝 .env 파일에 KAKAO_API_KEY를 설정해주세요!"
    
    try:
        # 1. 출발지 좌표 검색
        dep_coords = get_coordinates(departure, KAKAO_API_KEY)
        dest_coords = get_coordinates(destination, KAKAO_API_KEY)
        
        if not dep_coords or not dest_coords:
            debug_info = f"❌ 주소를 찾을 수 없습니다.\n\n"
            debug_info += f"🔍 디버그 정보:\n"
            debug_info += f"출발지 '{departure}' 좌표: {dep_coords}\n"
            debug_info += f"도착지 '{destination}' 좌표: {dest_coords}\n\n"
            debug_info += f"💡 해결 방법:\n"
            debug_info += f"• 정확한 주소를 입력해주세요 (예: 서울특별시 강남구)\n"
            debug_info += f"• 지하철역명 + '역'을 붙여주세요 (예: 강남역)\n"
            debug_info += f"• 유명한 건물명을 사용해보세요 (예: 롯데타워)"
            return debug_info
        
        # 2. 거리 계산
        distance = calculate_distance(dep_coords, dest_coords)
        estimated_time = max(int(distance * 2.5), 15)  # 대략적인 시간 계산
        
        result = f"🚇 {departure} → {destination}\n\n"
        result += f"📍 직선거리: {distance:.1f}km\n"
        result += f"⏱️ 예상 소요시간: {estimated_time}분\n\n"
        result += "🛤️ 추천 교통수단:\n"
        
        if distance < 2:
            result += "🚶‍♂️ 도보 이용 권장 (15-20분)\n"
        elif distance < 10:
            result += "🚌 [버스] 또는 [지하철] 이용\n"
            result += "🚇 환승 1회 예상\n"
        else:
            result += "🚇 [지하철] 또는 [버스] 이용 권장\n"
        
        result += f"\n📱 실시간 정보는 지하철앱을 확인하세요"
        
        return result
        
    except Exception as e:
        return f"❌ 교통 정보 조회 중 오류가 발생했습니다.\n오류: {str(e)}"

def get_coordinates(address, api_key):
    """주소를 좌표로 변환"""
    try:
        # 먼저 주소 검색 시도
        url = "https://dapi.kakao.com/v2/local/search/address.json"
        headers = {'Authorization': f'KakaoAK {api_key}'}
        params = {'query': address}
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        print(f"주소 검색 API 응답 상태: {response.status_code}")
        response.raise_for_status()
        data = response.json()
        print(f"주소 '{address}' 검색 결과: {len(data.get('documents', []))}개 발견")
        
        if data['documents']:
            doc = data['documents'][0]
            coords = float(doc['x']), float(doc['y'])
            print(f"좌표 변환 성공: {address} -> {coords}")
            return coords
        
        # 주소 검색 실패 시 키워드 검색 시도
        print(f"주소 검색 실패, 키워드 검색 시도: {address}")
        url = "https://dapi.kakao.com/v2/local/search/keyword.json"
        params = {'query': address}
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        print(f"키워드 '{address}' 검색 결과: {len(data.get('documents', []))}개 발견")
        
        if data['documents']:
            doc = data['documents'][0]
            coords = float(doc['x']), float(doc['y'])
            print(f"키워드 검색 성공: {address} -> {coords}")
            return coords
        
        print(f"'{address}' 좌표 검색 완전 실패")
        return None
        
    except requests.exceptions.RequestException as e:
        print(f"API 요청 오류 ({address}): {e}")
        return None
    except Exception as e:
        print(f"좌표 검색 일반 오류 ({address}): {e}")
        return None

def calculate_distance(coord1, coord2):
    """두 좌표 간의 거리 계산 (km)"""
    lat1, lon1 = coord1[1], coord1[0]
    lat2, lon2 = coord2[1], coord2[0]
    
    # 하버사인 공식
    R = 6371  # 지구의 반지름 (km)
    
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    
    a = (math.sin(dlat/2) * math.sin(dlat/2) + 
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * 
         math.sin(dlon/2) * math.sin(dlon/2))
    
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    distance = R * c
    
    return distance

def get_kma_weather_direct(location):
    """한국 기상청 API로 날씨 정보 직접 조회"""
    
    # 환경변수에서 기상청 API 키 가져오기
    KMA_API_KEY = os.getenv('KMA_API_KEY')
    
    if not KMA_API_KEY:
        return """🌤️ 한국 기상청 날씨 서비스
        
⚠️ 기상청 API 키가 설정되지 않았습니다.

📝 API 키 발급 방법:
1. https://data.go.kr 접속
2. 회원가입 및 로그인
3. '기상청_단기예보 조회서비스' 검색
4. 활용신청 → API 키 발급
5. .env 파일에 KMA_API_KEY 설정

💡 무료로 하루 1000건까지 사용 가능합니다!"""
    
    try:
        # 주요 도시 좌표 (기상청 격자 좌표)
        city_coords = {
            '서울': {'nx': 60, 'ny': 127, 'name': '서울특별시'},
            '부산': {'nx': 98, 'ny': 76, 'name': '부산광역시'},
            '대구': {'nx': 89, 'ny': 90, 'name': '대구광역시'},
            '인천': {'nx': 55, 'ny': 124, 'name': '인천광역시'},
            '광주': {'nx': 58, 'ny': 74, 'name': '광주광역시'},
            '대전': {'nx': 67, 'ny': 100, 'name': '대전광역시'},
            '울산': {'nx': 102, 'ny': 84, 'name': '울산광역시'},
            '세종': {'nx': 66, 'ny': 103, 'name': '세종특별자치시'},
            '수원': {'nx': 60, 'ny': 121, 'name': '경기도 수원'},
            '춘천': {'nx': 73, 'ny': 134, 'name': '강원도 춘천'},
            '청주': {'nx': 69, 'ny': 106, 'name': '충청북도 청주'},
            '전주': {'nx': 63, 'ny': 89, 'name': '전라북도 전주'},
            '포항': {'nx': 102, 'ny': 94, 'name': '경상북도 포항'},
            '제주': {'nx': 52, 'ny': 38, 'name': '제주특별자치도'}
        }
        
        # 도시 찾기
        coords = None
        city_name = location
        for city, coord in city_coords.items():
            if city in location:
                coords = coord
                city_name = coord['name']
                break
        
        if not coords:
            # 기본값: 서울
            coords = city_coords['서울']
            city_name = '서울특별시 (기본값)'
        
        # 기상청 API 호출
        now = datetime.now()
        base_date = now.strftime('%Y%m%d')
        
        # 발표시간 결정 (기상청은 매시 30분에 발표)
        if now.minute < 30:
            base_time = f"{now.hour-1:02d}30"
        else:
            base_time = f"{now.hour:02d}30"
        
        if base_time == "-130":
            base_time = "2330"
            base_date = (now.replace(day=now.day-1)).strftime('%Y%m%d')
        
        url = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtFcst"
        params = {
            'serviceKey': KMA_API_KEY,
            'pageNo': '1',
            'numOfRows': '60',
            'dataType': 'JSON',
            'base_date': base_date,
            'base_time': base_time,
            'nx': coords['nx'],
            'ny': coords['ny']
        }
        
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        # API 응답 확인
        header = data.get('response', {}).get('header', {})
        if header.get('resultCode') != '00':
            return f"⚠️ 기상청 API 오류\n코드: {header.get('resultCode')}\n메시지: {header.get('resultMsg')}"
        
        items = data.get('response', {}).get('body', {}).get('items', {}).get('item', [])
        
        if not items:
            return f"📍 {city_name} 날씨 데이터를 찾을 수 없습니다."
        
        # 시간대별 데이터 파싱
        hourly_data = {}
        for item in items:
            fcst_time = item['fcstTime']
            category = item['category']
            fcst_value = item['fcstValue']
            
            if fcst_time not in hourly_data:
                hourly_data[fcst_time] = {}
            hourly_data[fcst_time][category] = fcst_value
        
        # 모바일 친화적 포맷팅
        result = f"📍 {city_name}\n\n"
        
        # 현재 날씨 (간결하게)
        current_hour = now.strftime('%H00')
        if current_hour in hourly_data:
            current_data = hourly_data[current_hour]
            temp = current_data.get('T1H', 'N/A')
            sky = current_data.get('SKY', '1')
            pty = current_data.get('PTY', '0')
            humidity = current_data.get('REH', 'N/A')
            weather_emoji, weather_desc = get_kma_weather_status(sky, pty)
            
            result += f"🕐 지금: {weather_emoji} {weather_desc}"
            if temp != 'N/A':
                result += f" {temp}°C"
            if humidity != 'N/A':
                result += f" ({humidity}%)"
            result += "\n\n"
        
        # 시간대별 예보 (더 짧게)
        target_times = [
            ('0900', '🌅 오전'),
            ('1500', '☀️ 오후'),
            ('2100', '🌙 저녁')
        ]
        
        forecast_found = False
        for time_code, time_label in target_times:
            if time_code in hourly_data:
                if not forecast_found:
                    result += "📅 예보\n"
                    forecast_found = True
                    
                time_data = hourly_data[time_code]
                temp = time_data.get('T1H', 'N/A')
                sky = time_data.get('SKY', '1')
                pty = time_data.get('PTY', '0')
                
                weather_emoji, weather_desc = get_kma_weather_status(sky, pty)
                
                result += f"{time_label}: {weather_emoji} {weather_desc}"
                if temp != 'N/A':
                    result += f" {temp}°C"
                result += "\n"
        
        # 추가 정보 (선택적)
        if current_hour in hourly_data:
            current_data = hourly_data[current_hour]
            wind_speed = current_data.get('WSD', 'N/A')
            rainfall = current_data.get('RN1', '0')
            
            extras = []
            if wind_speed != 'N/A':
                extras.append(f"💨 {wind_speed}m/s")
            if rainfall != '0' and rainfall != 'N/A':
                extras.append(f"🌧️ {rainfall}mm")
            
            if extras:
                result += f"\n{' | '.join(extras)}\n"
        
        result += f"\n📊 기상청 ({base_date[4:6]}.{base_date[6:8]} {base_time[:2]}:{base_time[2:4]})"
        
        return result
        
    except requests.exceptions.RequestException as e:
        return f"🌐 기상청 API 연결 오류: {str(e)}"
    except Exception as e:
        return f"⚠️ 날씨 서비스 오류: {str(e)}"

def get_kma_weather_status(sky, pty):
    """기상청 코드를 날씨 상태로 변환"""
    # 강수형태 우선 체크 (PTY)
    if pty == '1':
        return '🌧️', '비'
    elif pty == '2':
        return '🌨️', '비/눈'
    elif pty == '3':
        return '❄️', '눈'
    elif pty == '4':
        return '⛈️', '소나기'
    
    # 하늘상태 체크 (SKY)
    if sky == '1':
        return '☀️', '맑음'
    elif sky == '3':
        return '⛅', '구름많음'
    elif sky == '4':
        return '☁️', '흐림'
    else:
        return '🌤️', '보통'


app = Flask(__name__)

CATEGORIES = ['날씨', '교통', '레시피', '주가', '명언']

def get_result(category, keyword=None, departure=None, destination=None):
    # 카테고리별로 실제 API 서비스 사용
    if category == '날씨':
        return get_kma_weather_direct(keyword)
    elif category == '교통':
        # 임시로 카카오 API 직접 구현
        return get_kakao_directions_direct(departure, destination)
    elif category == '주가':
        return krx_service.get_stock_info(keyword)
    elif category == '레시피':
        return recipe_service.get_recipe(keyword)
    elif category == '명언':
        return quote_service.get_quote(keyword)
    
    return "지원하지 않는 카테고리입니다."

def parse_recipe_result(result):
    """레시피 결과를 파싱하여 재료와 조리법을 분리"""
    parts = result.split('[조리법]')
    if len(parts) > 1:
        # 조리법 부분을 정규표현식으로 분리
        steps = re.split(r'\d+\.|\n', parts[1])
        steps = [step.strip() for step in steps if step.strip()]
        return {
            'ingredients': parts[0].strip(),
            'steps': steps
        }
    return {
        'ingredients': result,
        'steps': []
    }

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    parsed_recipe = None
    selected_category = CATEGORIES[0]
    keyword = ''
    departure = ''
    destination = ''

    if request.method == 'POST':
        selected_category = request.form.get('category')
        
        if selected_category == '교통':
            departure = request.form.get('departure', '').strip()
            destination = request.form.get('destination', '').strip()
            if departure and destination:
                result = get_result(selected_category, departure=departure, destination=destination)
        else:
            keyword = request.form.get('keyword', '').strip()
            if keyword:
                result = get_result(selected_category, keyword=keyword)
                if selected_category == '레시피':
                    parsed_recipe = parse_recipe_result(result)

    return render_template(
        'index.html',
        categories=CATEGORIES,
        selected_category=selected_category,
        result=result,
        parsed_recipe=parsed_recipe,
        keyword=keyword,
        departure=departure,
        destination=destination
    )

    


if __name__ == '__main__':
    app.run(debug=True)
import requests
import os
from datetime import datetime

class WeatherService:
    """한국 기상청 API를 사용한 날씨 정보 서비스"""
    
    def __init__(self):
        # 환경변수에서 기상청 API 키 가져오기
        self.api_key = os.getenv('KMA_API_KEY')
        self.base_url = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0"
    
    def get_weather(self, location):
        """지역의 현재 날씨 정보를 가져옵니다"""
        if not self.api_key:
            return "WeatherAPI 키가 설정되지 않았습니다."
        
        try:
            # 현재 날씨 + 시간별 예보
            url = f"{self.base_url}/forecast.json"
            params = {
                'key': self.api_key,
                'q': location,
                'days': 1,
                'aqi': 'no',
                'alerts': 'no',
                'lang': 'ko'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            current = data['current']
            forecast = data['forecast']['forecastday'][0]['hour']
            
            # 현재 시간 기준으로 오전, 오후, 저녁 예보 선별
            current_hour = datetime.now().hour
            morning = next((h for h in forecast if h['time'].endswith('09:00')), None)
            afternoon = next((h for h in forecast if h['time'].endswith('15:00')), None)
            evening = next((h for h in forecast if h['time'].endswith('21:00')), None)
            
            def get_weather_emoji(condition):
                """날씨 상태에 따른 이모지 반환"""
                condition_lower = condition.lower()
                if 'sunny' in condition_lower or '맑' in condition_lower:
                    return '☀️'
                elif 'rain' in condition_lower or '비' in condition_lower:
                    return '🌧️'
                elif 'cloud' in condition_lower or '구름' in condition_lower:
                    return '☁️'
                elif 'snow' in condition_lower or '눈' in condition_lower:
                    return '❄️'
                else:
                    return '🌤️'
            
            result = f"📍 {location} 날씨 정보\n\n"
            
            if morning:
                emoji = get_weather_emoji(morning['condition']['text'])
                result += f"{emoji} 오전(9시): {morning['condition']['text']}, {morning['temp_c']}°C\n"
            
            if afternoon:
                emoji = get_weather_emoji(afternoon['condition']['text'])
                result += f"{emoji} 오후(15시): {afternoon['condition']['text']}, {afternoon['temp_c']}°C\n"
                
            if evening:
                emoji = get_weather_emoji(evening['condition']['text'])
                result += f"{emoji} 저녁(21시): {evening['condition']['text']}, {evening['temp_c']}°C\n"
            
            result += f"\n💨 현재 바람: {current['wind_kph']}km/h"
            result += f"\n💧 현재 습도: {current['humidity']}%"
            
            return result
            
        except requests.exceptions.RequestException as e:
            return f"날씨 정보를 가져올 수 없습니다: {str(e)}"
        except KeyError as e:
            return f"날씨 데이터 형식 오류: {str(e)}"
        except Exception as e:
            return f"날씨 서비스 오류: {str(e)}"


class KakaoMapService:
    """카카오맵 API를 사용한 교통 정보 서비스"""
    
    def __init__(self):
        # 환경변수에서 카카오 API 키 가져오기
        self.api_key = os.getenv('KAKAO_API_KEY')
        self.base_url = "https://dapi.kakao.com/v2/local"
        self.directions_url = "https://apis-navi.kakaomobility.com/v1/directions"
    
    def get_directions(self, departure, destination):
        """출발지에서 도착지까지의 경로 정보를 가져옵니다"""
        if not self.api_key:
            return "카카오 API 키가 설정되지 않았습니다."
        
        try:
            # 1. 주소를 좌표로 변환
            dep_coords = self._get_coordinates(departure)
            dest_coords = self._get_coordinates(destination)
            
            if not dep_coords or not dest_coords:
                return f"주소를 찾을 수 없습니다. ({departure} 또는 {destination})"
            
            # 2. 경로 검색 (대중교통)
            headers = {
                'Authorization': f'KakaoAK {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            # 카카오 모빌리티 API 사용 (실제로는 더 복잡한 설정 필요)
            # 여기서는 간단한 직선거리 계산으로 대체
            distance = self._calculate_distance(dep_coords, dest_coords)
            estimated_time = max(int(distance * 2), 15)  # 대략적인 시간 계산
            
            result = f"🚉 {departure} → {destination}\n\n"
            result += f"📍 예상 소요시간: {estimated_time}분\n"
            result += f"📏 직선거리: {distance:.1f}km\n\n"
            result += "🚇 추천 경로:\n"
            result += "• 지하철 이용 시 환승 1-2회 예상\n"
            result += "• 버스 이용 시 1회 환승 예상\n"
            result += "• 실시간 교통상황에 따라 변동 가능"
            
            return result
            
        except Exception as e:
            return f"교통 정보를 가져올 수 없습니다: {str(e)}"
    
    def _get_coordinates(self, address):
        """주소를 좌표로 변환"""
        try:
            url = f"{self.base_url}/search/address.json"
            headers = {'Authorization': f'KakaoAK {self.api_key}'}
            params = {'query': address}
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data['documents']:
                doc = data['documents'][0]
                return float(doc['x']), float(doc['y'])  # 경도, 위도
            return None
            
        except Exception:
            return None
    
    def _calculate_distance(self, coord1, coord2):
        """두 좌표 간의 거리 계산 (km)"""
        import math
        
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


class KRXStockService:
    """공공데이터포털 한국거래소 API를 사용한 주가 정보 서비스"""
    
    def __init__(self):
        # 환경변수에서 공공데이터포털 API 키 가져오기
        self.api_key = os.getenv('STOCK_API_KEY')
        self.base_url = "http://apis.data.go.kr/1160100/service/GetStockSecuritiesInfoService"
    
    def get_stock_info(self, stock_name):
        """주식 정보를 가져옵니다"""
        if not self.api_key:
            return "공공데이터포털 API 키가 설정되지 않았습니다."
        
        try:
            # 1. 종목 코드 검색
            stock_code = self._search_stock_code(stock_name)
            if not stock_code:
                return f"'{stock_name}' 종목을 찾을 수 없습니다.\n💡 정확한 종목명을 입력해주세요 (예: 삼성전자, SK하이닉스)"
            
            # 2. 주가 정보 조회
            stock_data = self._get_stock_price(stock_code)
            if not stock_data:
                return "주가 정보를 가져올 수 없습니다."
            
            # 3. 결과 포맷팅
            return self._format_stock_info(stock_name, stock_code, stock_data)
            
        except Exception as e:
            return f"주가 정보 조회 중 오류가 발생했습니다: {str(e)}"
    
    def _search_stock_code(self, stock_name):
        """종목명으로 종목코드 검색"""
        # 주요 종목 코드 매핑
        stock_codes = {
            '삼성전자': '005930',
            'SK하이닉스': '000660',
            'NAVER': '035420',
            '네이버': '035420',
            '카카오': '035720',
            'LG화학': '051910',
            '현대차': '005380',
            '현대자동차': '005380',
            'POSCO홀딩스': '005490',
            '포스코': '005490',
            '한국전력': '015760',
            '셀트리온': '068270',
            'LG전자': '066570',
            '기아': '000270',
            '삼성바이오로직스': '207940',
            'SK이노베이션': '096770',
            '현대모비스': '012330',
            '삼성SDI': '006400'
        }
        
        return stock_codes.get(stock_name)
    
    def _get_stock_price(self, stock_code):
        """종목코드로 주가 정보 조회"""
        try:
            # 공공데이터포털 한국거래소 상장정보 API
            url = f"{self.base_url}/getStockPriceInfo"
            params = {
                'serviceKey': self.api_key,
                'numOfRows': '1',
                'pageNo': '1',
                'resultType': 'json',
                'likeSrtnCd': stock_code
            }
            
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            
            # JSON 응답 파싱
            if response.text.strip().startswith('<'):
                # XML 응답인 경우
                return self._parse_xml_stock_response(response.text)
            else:
                data = response.json()
                
                # API 응답 구조 확인
                if 'response' in data:
                    header = data.get('response', {}).get('header', {})
                    if header.get('resultCode') != '00':
                        return None
                    
                    items = data.get('response', {}).get('body', {}).get('items', {})
                    if isinstance(items, dict) and 'item' in items:
                        items = items['item']
                        return items[0] if isinstance(items, list) and items else items
                
                return None
            
        except Exception as e:
            print(f"주가 API 호출 오류: {e}")
            return None
    
    def _parse_xml_stock_response(self, xml_text):
        """XML 응답을 파싱합니다"""
        try:
            import xml.etree.ElementTree as ET
            root = ET.fromstring(xml_text)
            
            # XML에서 오류 코드 확인
            result_code = root.find('.//resultCode')
            if result_code is not None and result_code.text != '00':
                return None
            
            # 데이터 항목 찾기
            items = root.findall('.//item')
            if items:
                item = items[0]
                return {
                    'mrktCtg': item.find('mrktCtg').text if item.find('mrktCtg') is not None else '',
                    'clpr': item.find('clpr').text if item.find('clpr') is not None else '0',
                    'vs': item.find('vs').text if item.find('vs') is not None else '0',
                    'fltRt': item.find('fltRt').text if item.find('fltRt') is not None else '0'
                }
            
            return None
            
        except Exception:
            return None
    
    def _format_stock_info(self, stock_name, stock_code, stock_data):
        """주가 정보를 포맷팅합니다"""
        try:
            # 현재가와 등락 정보 추출
            current_price = int(stock_data.get('clpr', 0))  # 종가
            change_amount = int(stock_data.get('vs', 0))    # 전일대비
            change_rate = float(stock_data.get('fltRt', 0)) # 등락률
            
            # 등락 방향 결정
            if change_rate > 0:
                emoji = "📈"
                sign = "+"
                color = "🔴"
            elif change_rate < 0:
                emoji = "📉"
                sign = ""
                color = "🔵"
            else:
                emoji = "📊"
                sign = ""
                color = "⚪"
            
            result = f"{emoji} {stock_name} ({stock_code})\n\n"
            result += f"💰 현재가: {current_price:,}원\n"
            result += f"{color} 전일대비: {sign}{change_amount:,}원\n"
            result += f"📊 등락률: {sign}{change_rate:.2f}%\n"
            result += f"📅 업데이트: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
            result += f"📈 거래소: {stock_data.get('mrktCtg', 'KRX')}"
            
            return result
            
        except Exception as e:
            return f"주가 정보 포맷팅 오류: {str(e)}"


class RecipeService:
    """OpenAI API를 사용한 레시피 서비스"""
    
    def __init__(self):
        # OpenAI API 키 설정
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
    
    def get_recipe(self, food_name):
        """음식 이름으로 레시피 정보를 가져옵니다 - OpenAI Chain 사용"""
        if not self.openai_api_key:
            return f"🍳 {food_name} 레시피\n\n⚠️ OpenAI API 키가 설정되지 않았습니다.\n📝 OpenAI API 키 설정: 환경변수 OPENAI_API_KEY에 키 입력"
        
        try:
            from openai import OpenAI
            
            # OpenAI 클라이언트 초기화 (v1.0+ 방식)
            client = OpenAI(api_key=self.openai_api_key)
            
            # Chain 1: 레시피 기본 정보 생성
            basic_prompt = f"""
            '{food_name}' 요리의 레시피를 한국어로 작성해주세요.
            
            다음 형식으로 작성해주세요:
            🍳 [음식명] 레시피
            
            📊 영양 정보 (1인분당)
            • 칼로리: [칼로리]kcal
            • 단백질: [단백질]g
            • 지방: [지방]g
            • 탄수화물: [탄수화물]g
            
            🥘 재료 ([인분]분)
            • [재료명] [양]
            • [재료명] [양]
            ...
            
            👩‍🍳 조리법
            1. [단계별 설명]
            2. [단계별 설명]
            ...
            
            💡 요리 팁
            • [유용한 팁]
            
            정확하고 실용적인 레시피를 제공해주세요.
            """
            
            response1 = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "당신은 전문 요리사입니다. 정확하고 따라하기 쉬운 레시피를 제공합니다."},
                    {"role": "user", "content": basic_prompt}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            
            basic_recipe = response1.choices[0].message.content.strip()
            
            # Chain 2: 레시피 개선 및 추가 정보
            improvement_prompt = f"""
            다음 레시피를 검토하고 개선해주세요:
            
            {basic_recipe}
            
            개선 사항:
            1. 조리 시간과 난이도 추가
            2. 대체 재료 제안
            3. 보관 방법 추가
            4. 더 자세한 조리 팁
            
            개선된 레시피를 제공해주세요.
            """
            
            response2 = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "당신은 레시피 검토 전문가입니다. 레시피를 더 완벽하고 실용적으로 만듭니다."},
                    {"role": "user", "content": improvement_prompt}
                ],
                max_tokens=1200,
                temperature=0.5
            )
            
            improved_recipe = response2.choices[0].message.content.strip()
            
            return improved_recipe
            
        except Exception as e:
            return f"🍳 {food_name} 레시피\n\n❌ OpenAI API 오류: {str(e)}\n\n💡 API 키를 확인하고 다시 시도해주세요."


class QuoteService:
    """OpenAI API를 사용한 명언 서비스"""
    
    def __init__(self):
        # OpenAI API 키 설정
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
    
    def get_quote(self, keyword=None):
        """키워드에 맞는 명언을 생성합니다"""
        if not self.openai_api_key:
            return self._get_sample_quote(keyword)
        
        try:
            from openai import OpenAI
            
            # OpenAI 클라이언트 초기화
            client = OpenAI(api_key=self.openai_api_key)
            
            # 키워드가 있는 경우와 없는 경우 구분
            if keyword and keyword.strip():
                prompt = f"""
                '{keyword}'와 관련된 의미있고 감동적인 명언을 만들어주세요.
                
                다음 형식으로 작성해주세요:
                💫 오늘의 명언
                
                "[명언 내용]"
                
                - 작가 또는 인물명
                
                💡 해설
                [명언의 의미와 어떻게 적용할 수 있는지 간단히 설명]
                
                한국어로 작성하고, 실제 존재하는 명언이거나 그와 비슷한 수준의 깊이 있는 내용으로 만들어주세요.
                """
            else:
                prompt = """
                오늘 하루를 시작하거나 마무리할 때 도움이 되는 감동적이고 의미있는 명언을 만들어주세요.
                
                다음 형식으로 작성해주세요:
                💫 오늘의 명언
                
                "[명언 내용]"
                
                - 작가 또는 인물명
                
                💡 해설
                [명언의 의미와 어떻게 적용할 수 있는지 간단히 설명]
                
                한국어로 작성하고, 실제 존재하는 명언이거나 그와 비슷한 수준의 깊이 있는 내용으로 만들어주세요.
                """
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "당신은 지혜로운 철학자이자 작가입니다. 사람들에게 영감을 주는 깊이 있는 명언을 제공합니다."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.8
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return f"💫 명언 서비스\n\n❌ OpenAI API 오류: {str(e)}\n\n💡 API 키를 확인하고 다시 시도해주세요."
    
    def _get_sample_quote(self, keyword=None):
        """OpenAI API 키가 없을 때 샘플 명언 제공"""
        sample_quotes = [
            {
                'quote': '성공은 최종 목적지가 아니라 여행하는 과정이다.',
                'author': '아리스토텔레스',
                'meaning': '결과보다는 과정에서 배우고 성장하는 것이 진정한 성공의 의미입니다.'
            },
            {
                'quote': '어제는 역사가 되었고, 내일은 신비로우며, 오늘은 선물이다.',
                'author': '엘리너 루스벨트',
                'meaning': '과거에 얽매이거나 미래를 걱정하기보다는 현재에 집중하며 살아가는 것이 중요합니다.'
            },
            {
                'quote': '자신의 한계를 뛰어넘는 것은 타인과의 경쟁이 아닌 어제의 나와의 경쟁이다.',
                'author': '괴테',
                'meaning': '다른 사람과 비교하기보다는 어제의 자신보다 나은 사람이 되기 위해 노력하는 것이 진정한 성장입니다.'
            }
        ]
        
        import random
        selected_quote = random.choice(sample_quotes)
        
        result = "💫 오늘의 명언\n\n"
        result += "⚠️ OpenAI API 키가 설정되지 않았습니다.\n"
        result += "기본 명언을 제공합니다.\n\n"
        result += f'"{selected_quote["quote"]}"\n\n'
        result += f'- {selected_quote["author"]}\n\n'
        result += f'💡 해설\n{selected_quote["meaning"]}\n\n'
        result += "📝 더 다양한 명언을 원하시면 OpenAI API 키를 설정해주세요!"
        
        return result


# API 서비스 인스턴스들
weather_service = WeatherService()
kakao_service = KakaoMapService()
krx_service = KRXStockService()
recipe_service = RecipeService()
quote_service = QuoteService()

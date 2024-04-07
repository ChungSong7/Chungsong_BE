from rest_framework.views import APIView
from rest_framework.response import Response
from bs4 import BeautifulSoup
import requests
from datetime import datetime, timedelta

class MenuView(APIView):
    def get(self, request, format=None):


        # 현재 날짜를 얻습니다.
        current_date = datetime.now().date()

        # 시작 날짜를 현재 날짜 기준으로 3일 전으로 설정합니다.
        start_date = current_date - timedelta(days=3)

        # 끝 날짜를 현재 날짜 기준으로 3일 후로 설정합니다.
        end_date = current_date + timedelta(days=3)

        # 시작 날짜와 끝 날짜를 문자열 형식으로
        start_date_str = start_date.strftime('%Y-%m-%d')
        end_date_str = end_date.strftime('%Y-%m-%d')
        
        #url
        base_url = 'https://www.ndhs.or.kr/site/main/schedule/calendar/week_menu_EP'
        url1 = f'{base_url}?date={start_date_str}'
        url2 = f'{base_url}?date={end_date_str}'
        
        # URL 요청
        response1 = requests.get(url1)
        response2 = requests.get(url2)
        html1 = response1.text
        html2 = response2.text
        soup1 = BeautifulSoup(html1, 'html.parser')
        soup2 = BeautifulSoup(html2, 'html.parser')
        
    
        menu_dict = {}
        
        # 웹페이지에서 메뉴 정보를 파싱
        for soup in [soup1, soup2]:
            meal_wrap = soup.find('div', class_='mealWrap')
            for meal_row in meal_wrap.find_all('li', class_='flex-tb'):
                date = meal_row.find('div', class_='date').text.strip()
                day = meal_row.find('div', class_='day').text.strip()
                breakfast = meal_row.find('div', class_='breakfast').find('span', class_='flex-inner').text.strip().split('\r\n')
                lunch = meal_row.find('div', class_='lunch').find('span', class_='flex-inner').text.strip().split('\r\n')
                dinner = meal_row.find('div', class_='dinner').find('span', class_='flex-inner').text.strip().split('\r\n')


                menu_dict[date] = {
                    'day': day,
                    'breakfast': breakfast,
                    'lunch': lunch,
                    'dinner': dinner
                }
        selected_menu={}
        for date_str in menu_dict.keys():
            # 만약 현재 날짜 기준으로 start_date_str과 end_date_str 사이에 해당하는 키라면 dict_B에 추가
            if start_date_str <= date_str <= end_date_str:
                selected_menu[date_str] = menu_dict[date_str]
        return Response(selected_menu)

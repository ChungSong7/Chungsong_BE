from rest_framework.views import APIView
from rest_framework.response import Response
from bs4 import BeautifulSoup
import requests

class MenuView(APIView):
    def get(self, request, format=None):
        url = 'https://www.ndhs.or.kr/site/main/schedule/calendar/week_menu_EP'  # 해당 사이트의 URL을 입력합니다
        response = requests.get(url)
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        
        menu_list = []
        meal_wrap = soup.find('div', class_='mealWrap')
        for meal_row in meal_wrap.find_all('li', class_='flex-tb'):
            date = meal_row.find('div', class_='date').text.strip()
            day = meal_row.find('div', class_='day').text.strip()
            breakfast = meal_row.find('div', class_='breakfast').find('span', class_='flex-inner').text.strip().split('\r\n')
            lunch = meal_row.find('div', class_='lunch').find('span', class_='flex-inner').text.strip().split('\r\n')
            dinner = meal_row.find('div', class_='dinner').find('span', class_='flex-inner').text.strip().split('\r\n')
            
            menu_list.append({
                'date': date,
                'day': day,
                'breakfast': breakfast,
                'lunch': lunch,
                'dinner': dinner
            })
            

            menu_dict = {}
            for menu_item in menu_list:
                date = menu_item['date']
                menu_dict[date] = {
                'day': menu_item['day'],
                'breakfast': menu_item['breakfast'],
                'lunch': menu_item['lunch'],
                'dinner': menu_item['dinner']
    }
        
        return Response(menu_dict)

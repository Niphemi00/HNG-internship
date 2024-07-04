# from django.shortcuts import render

# from rest_framework import generics
# from rest_framework.response import Response
# from rest_framework import status
# import requests
# from django.conf import settings
# # from rest_framework import serializers
# from .serializers import VisitorSerializer


# geoLocationService = settings.IP2LOCATION_API_KEY
# weatherAPiService = settings.OPENWEATHER_API_KEY


# class VisitorsView(generics.GenericAPIView):
#   def get_user_ip(self, request):
#     x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
#     if x_forwarded_for:
#       ip = x_forwarded_for.split(',')[0]
#     else:
#       ip = request.META.get('REMOTE_ADDR', '127.0.0.1')
#       return ip
#   def get(self, request):
#     visitor_name = request.query_params.get('visitor_name', 'Guest')
#     client_ip = self.get_user_ip(request)
#     # location_response
#     location_response = requests.get(f'http://api.ipstack.com/{client_ip}?access_key={geoLocationService}')
#     location_response_data = location_response.json()
#     print(location_response_data)
#     city = location_response_data.get('city_name', 'Unknown')
    # #weather response
    # openweather__api_key = weatherAPiService
    # weather_response = requests.get(f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={openweather__api_key}')
    # weather_response_data = weather_response.json()
    # print(weather_response_data)
    # temperature = weather_response_data['main']['temp'] if 'main' in weather_response_data else 'unknown'
    # response = {
    #             "client_ip": client_ip,
    #             "location": city,
    #             "greeting": f"Hello, {visitor_name}!, the temperature is {temperature} degrees Celsius in {city}"
    #         }
    # #serializing
#     serializer = VisitorSerializer(data=response)
#     if serializer.is_valid():
#       return Response(serializer.data, status=status.HTTP_200_OK)
#     else:
#       return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# visitor_view = VisitorsView.as_view()

from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
import requests
from django.conf import settings
from .serializers import VisitorSerializer

geoLocationService = settings.IP2LOCATION_API_KEY
weatherAPiService = settings.OPENWEATHER_API_KEY

class VisitorsView(generics.GenericAPIView):
    def get_user_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR', '127.0.0.1')
        return ip

    def get(self, request):
        visitor_name = request.query_params.get('visitor_name', 'Guest')
        client_ip = self.get_user_ip(request)

        try:
            # location_response
            location_response = requests.get(f'https://api.ipfind.com/?ip={client_ip}&auth={geoLocationService}')
            location_response_data = location_response.json()
            print(location_response_data)
            city = location_response_data.get('city_name', 'unknown')
            #get location
            

            #weather response
            openweather__api_key = weatherAPiService
            weather_response = requests.get(f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={openweather__api_key}')
            weather_response_data = weather_response.json()
            print(weather_response_data)
            temperature = weather_response_data['main']['temp'] if 'main' in weather_response_data else '11'
            response = {
                        "client_ip": client_ip,
                        "location": city,
                        "greeting": f"Hello, {visitor_name}!, the temperature is {temperature} degrees Celsius in {city}"
                    }
            #serializing
            serializer = VisitorSerializer(data=response)
            if serializer.is_valid():
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except requests.exceptions.RequestException as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

visitor_view = VisitorsView.as_view()
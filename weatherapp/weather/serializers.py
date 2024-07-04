# 
from rest_framework import serializers

class VisitorSerializer(serializers.Serializer):
    client_ip = serializers.IPAddressField()
    location = serializers.CharField(max_length=100)
    greeting = serializers.CharField(max_length=200)
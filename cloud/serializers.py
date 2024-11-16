from rest_framework import serializers
from .models import S3Config
from .forms import FileUploadForm

class S3ConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = S3Config
        fields = ['access_key', 'secret_key', 'bucket_name', 'end_point']

class FileUploadSerializer(serializers.Serializer):
    file = serializers.FileField()

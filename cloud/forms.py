from django import forms
from django.core.exceptions import ValidationError

from cloud.models import S3Config


class S3ConfigForm(forms.ModelForm):
    class Meta:
        model = S3Config
        fields = ['access_key', 'secret_key', 'bucket_name', 'end_point']


class FileUploadForm(forms.Form):
    file = forms.FileField()

    def clean_file(self):
        file = self.cleaned_data.get('file')
        MAX_UPLOAD_SIZE = 5 * 1024 * 1024  # 设置最大上传文件大小为 5MB

        if file and file.size > MAX_UPLOAD_SIZE:
            raise ValidationError("文件大小超出限制！")
        return file

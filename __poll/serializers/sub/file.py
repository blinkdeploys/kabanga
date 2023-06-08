from rest_framework import serializers


ALLOWED_FILE_TYPES = ['image/png', 'image/jpeg', 'image/gif', 'application/pdf']
MAX_FILE_SIZE = 2 * 1024 * 1024  # 2MB

class FileUploadSerializer(serializers.Serializer):
    file = serializers.FileField(
        allow_empty_file=False,
        max_length=100,
        allow_null=True,
        required=False,
    )

    def validate_file(self, value):
        if value:
            if value.content_type not in ALLOWED_FILE_TYPES:
                raise serializers.ValidationError("Only PNG, JPEG and PDF files are allowed.")
            if value.size > MAX_FILE_SIZE:
                raise serializers.ValidationError("File size exceeds the maximum limit.")
        return value

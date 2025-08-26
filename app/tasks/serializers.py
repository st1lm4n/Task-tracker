from rest_framework import serializers
from .models import Task
from users.models import User

class TaskSerializer(serializers.ModelSerializer):
    # Поля только для чтения, чтобы отображать информацию об исполнителе и авторе
    executor_info = serializers.SerializerMethodField(read_only=True)
    author_info = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Task
        fields = '__all__'
        # Указываем, что executor и author передаются по id (PrimaryKeyRelatedField)
        # Но отображаем дополнительную информацию через executor_info и author_info
        extra_kwargs = {
            'executor': {'write_only': True},
            'author': {'write_only': True, 'required': False} # author будет задаваться автоматически
        }

    def get_executor_info(self, obj):
        return f"{obj.executor.username} ({obj.executor.get_role_display()})"

    def get_author_info(self, obj):
        return f"{obj.author.username} ({obj.author.get_role_display()})"

    def create(self, validated_data):
        # При создании задачи автор берется из запроса (request.user)
        request = self.context.get('request')
        validated_data['author'] = request.user
        return super().create(validated_data)
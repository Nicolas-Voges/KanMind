from rest_framework import serializers
from kanban_app.models import Board, Task, Comment
from user_auth_app.models import UserAccount
from user_auth_app.api.serializers import UserAccountSerializer
from django.contrib.auth.models import User


class BoardSerializer(serializers.ModelSerializer):
    member_count = serializers.SerializerMethodField()
    ticket_count = serializers.SerializerMethodField()
    tasks_to_do_count = serializers.SerializerMethodField()
    tasks_high_prio_count = serializers.SerializerMethodField()

    class Meta:
        model = Board
        fields = ['id',
                  'title',
                  'member_count',
                  'ticket_count',
                  'tasks_to_do_count',
                  'tasks_high_prio_count',
                  'owner_id',
                  'members',
                  'members_data'
        ]

        read_only_fields = [
            'owner_id',
            'member_count',
            'ticket_count',
            'tasks_to_do_count',
            'tasks_high_prio_count',
            'members_data'
        ]

    members = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.objects.all(),
        write_only=True,
    )

    members_data = UserAccountSerializer(many=True, read_only=True, source='members')

    def get_member_count(self, obj):
        return obj.members.count()
    
    def get_ticket_count(self, obj):
        return obj.tasks.count()

    def get_tasks_to_do_count(self, obj):
        return obj.tasks.filter(status=0).count()

    def get_tasks_high_prio_count(self, obj):
        return obj.tasks.filter(priority=2).count()
    

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        request = self.context.get('request')

        if request and request.method != 'PATCH':
            rep.pop('members_data', None)

        return rep
    


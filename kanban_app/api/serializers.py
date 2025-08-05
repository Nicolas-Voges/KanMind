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
                  'members'
        ]

        read_only_fields = [
            'owner_id',
            'member_count',
            'ticket_count',
            'tasks_to_do_count',
            'tasks_high_prio_count'
        ]

    members = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.objects.all(),
        write_only=True
    )


    def get_member_count(self, obj):
        return obj.members.count()
    
    def get_ticket_count(self, obj):
        return obj.tasks.count()

    def get_tasks_to_do_count(self, obj):
        return obj.tasks.filter(status=0).count()

    def get_tasks_high_prio_count(self, obj):
        return obj.tasks.filter(priority=2).count()
    
    # def to_representation(self, instance):
    #     rep = super().to_representation(instance)
    #     ordered = {
    #             'id': rep.get('id'),
    #             'title': rep.get('title'),
    #             'owner_id': rep.get('owner_id'),
    #             'owner_data': rep.get('owner_data'),
    #             'members': rep.get('members'),
    #             'members_data': rep.get('members_data'),
    #             'tasks': rep.get('tasks'),
    #         }
    #     return ordered
    
class TaskSerializer(serializers.ModelSerializer):
    
    class Meta:
        model=Task
        fields= [
            'id',
            'board',
            'title',
            'description',
            'status',
            'priority',
            'assignee',
            'assignee_id',
            'reviewer',
            'reviewer_id',
            'due_date',
        ]
        ordered=True

    assignee = UserAccountSerializer(read_only=True)
    assignee_id = serializers.PrimaryKeyRelatedField(
        source='assignee',
        queryset=User.objects.all(),
        write_only=True,
        required=False
    )

    reviewer = UserAccountSerializer(read_only=True)
    reviewer_id = serializers.PrimaryKeyRelatedField(
        source='reviewer',
        queryset=User.objects.all(),
        write_only=True,
        required=False
    )


    def to_representation(self, instance):
        rep = super().to_representation(instance)
        request = self.context.get('request')

        

        if request and request.method == 'POST':
            ordered = {
                'id': rep.get('id'),
                'board': rep.get('board'),
                'title': rep.get('title'),
                'description': rep.get('description'),
                'status': rep.get('status'),
                'priority': rep.get('priority'),
                'assignee': rep.get('assignee'),
                'reviewer': rep.get('reviewer'),
                'due_date': rep.get('due_date'),
            }
            ordered['comments_count'] = instance.comments.count()
            return ordered
        elif request and request.method == 'GET':
            ordered = {
                'id': rep.get('id'),
                'title': rep.get('title'),
                'description': rep.get('description'),
                'status': rep.get('status'),
                'priority': rep.get('priority'),
                'assignee': rep.get('assignee'),
                'reviewer': rep.get('reviewer'),
                'due_date': rep.get('due_date'),
            }
            ordered['comments_count'] = instance.comments.count()
            return ordered
        return rep
class BoardDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Board
        fields = ['id',
                  'title',
                  'owner_id',
                  'owner_data',
                  'members',
                  'members_data',
                  'tasks'
        ]

        read_only_fields = [
            'owner_id',
            'owner_data',
            'members_data',
            'tasks'
        ]

    members = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.objects.all(),
        write_only=True
    )
    members_data = UserAccountSerializer(many=True, read_only=True, source='members')
    owner_data = UserAccountSerializer(read_only=True, source='owner')
    tasks = TaskSerializer(many=True, read_only=True)

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        request = self.context.get('request')

        if request and request.method != 'PATCH':
            rep['members'] = rep.pop('members_data', None)
            rep.pop('owner_data', None)
            ordered = {
                'id': rep.get('id'),
                'title': rep.get('title'),
                'owner_id': rep.get('owner_id'),
                # 'owner_data': rep.get('owner_data'),
                'members': rep.get('members'),
                # 'members_data': rep.get('members_data'),
                'tasks': rep.get('tasks'),
            }
            return ordered

        else:
            rep.pop('owner_id', None)
            rep.pop('tasks', None)
            # ordered = {
            #     'id': rep.get('id'),
            #     'title': rep.get('title'),
            #     'owner_id': rep.get('owner_id'),
            #     'owner_data': rep.get('owner_data'),
            #     'members': rep.get('members'),
            #     'members_data': rep.get('members_data'),
            #     'tasks': rep.get('tasks'),
            # }

        return rep
    



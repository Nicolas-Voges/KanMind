from rest_framework import serializers
from django.contrib.auth.models import User
from user_auth_app.api.serializers import UserAccountSerializer
from user_auth_app.models import UserAccount
from kanban_app.models import Board, Task, Comment


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
        return obj.tasks.filter(status="to-do").count()

    def get_tasks_high_prio_count(self, obj):
        return obj.tasks.filter(priority="high").count()
    
    
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
            'creator'
        ]

        read_only_fields = [
            'creator'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')

        if request and request.method != 'POST':
            self.fields['board'].read_only = True

    assignee = UserAccountSerializer(read_only=True)
    assignee_id = serializers.PrimaryKeyRelatedField(
        source='assignee',
        queryset=User.objects.all(),
        write_only=True,
        required=False,
        allow_null=True
    )

    reviewer = UserAccountSerializer(read_only=True)
    reviewer_id = serializers.PrimaryKeyRelatedField(
        source='reviewer',
        queryset=User.objects.all(),
        write_only=True,
        required=False,
        allow_null=True
    )

    creator = serializers.PrimaryKeyRelatedField(
        read_only=True,
        required=False,
        allow_null=True
    )

    def validate(self, data):
        board = data.get('board') or getattr(self.instance, 'board', None)
        assignee = data.get('assignee')
        reviewer = data.get('reviewer')

        if not board:
            raise serializers.ValidationError("Board is required to validate members.")

        if assignee is not None and assignee not in board.members.all():
            raise serializers.ValidationError({"assignee_id": "Assignee must be a member of the board."})

        if reviewer is not None and reviewer not in board.members.all():
            raise serializers.ValidationError({"reviewer_id": "Reviewer must be a member of the board."})

        return data


    def to_representation(self, instance):
        rep = super().to_representation(instance)
        request = self.context.get('request')
        path = request.path

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
        if request and request.method != 'PATCH':
            ordered['comments_count'] = instance.comments.count()
        
        if request and request.method == 'GET' and '/boards/' in path or request.method in ['PATCH', 'PUT']:
            ordered.pop('board', None)
        return ordered
    

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
                'members': rep.get('members'),
                'tasks': rep.get('tasks'),
            }
            return ordered

        else:
            rep.pop('owner_id', None)
            rep.pop('tasks', None)

        return rep


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = [
            'id',
            'created_at',
            'author',
            'content'
        ]

        read_only_fields = [
            'id',
            'created_at',
            'author'
        ]

    
    def to_representation(self, instance):
        rep = super().to_representation(instance)
        author = User.objects.get(id=instance.author.id)
        rep['author'] = author.username

        ordered = {
            'id': rep.get('id'),
            'created_at': rep.get('created_at'),
            'author': rep.get('author'),
            'content': rep.get('content')
        }
        return ordered

"""
Serializers for the Kanban application API.

This module defines serializers for converting Board, Task, and Comment
model instances to and from JSON for API endpoints. It also includes
custom computed fields, validation rules, and data formatting for
enhanced API responses.

Classes:
    BoardSerializer: Serializer for basic board information and
        computed task/member counts.
    TaskSerializer: Serializer for task details, including assignee and
        reviewer validation.
    BoardDetailSerializer: Detailed serializer for boards, including
        nested task and member data.
    CommentSerializer: Serializer for comments, including author
        username formatting.
"""

from rest_framework import serializers
from django.contrib.auth.models import User
from user_auth_app.api.serializers import UserAccountSerializer
from kanban_app.models import Board, Task, Comment


class BoardSerializer(serializers.ModelSerializer):
    """
    Serializer for the Board model.

    Provides basic board data along with computed fields such as member
    count, ticket count, tasks to do, and high-priority tasks.
    """

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
        """
        Return the number of members in the board.
        """
        return obj.members.count()
    

    def get_ticket_count(self, obj):
        """
        Return the total number of tasks associated with the board.
        """
        return obj.tasks.count()


    def get_tasks_to_do_count(self, obj):
        """
        Return the number of tasks with a 'to-do' status.
        """
        return obj.tasks.filter(status="to-do").count()


    def get_tasks_high_prio_count(self, obj):
        """
        Return the number of high-priority tasks for the board.
        """
        return obj.tasks.filter(priority="high").count()
    
    
class TaskSerializer(serializers.ModelSerializer):
    """
    Serializer for the Task model.

    Includes related user information for assignee and reviewer,
    custom validation to ensure they belong to the board, and
    dynamic field ordering in the response.
    """

    
    title = serializers.CharField(required=True, allow_blank=False)
    board = serializers.PrimaryKeyRelatedField(
        queryset=Board.objects.all(),
        required=True)
    priority = serializers.CharField(required=True, allow_blank=False)
    status = serializers.CharField(required=True, allow_blank=False)
    due_date = serializers.DateField(required=True, allow_null=False)

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
        """
        Initialize the serializer and make the board field read-only
        for non-POST requests.
        """
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
        """
        Ensure that the assignee and reviewer (if provided) are members
        of the associated board.
        """
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
        """
        Customize the representation of the task.

        Adds a `comments_count` field for non-PATCH requests and removes
        the `board` field in certain GET, PATCH, and PUT contexts.
        """
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
    """
    Detailed serializer for the Board model.

    Includes full member and owner data, as well as nested tasks.
    """


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
        """
        Customize board representation.

        For non-PATCH requests, replaces `members` with detailed member
        data and removes `owner_data`. For PATCH requests, removes
        `owner_id` and `tasks`.
        """
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
    """
    Serializer for the Comment model.

    Converts comment author IDs into usernames for display in API
    responses.
    """


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
        """
        Customize comment representation to include the author's
        username instead of their ID.
        """
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
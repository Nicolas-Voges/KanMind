from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from user_auth_app.models import UserAccount

class Board(models.Model):
    title = models.CharField(max_length=63)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='boards_as_owner')
    members = models.ManyToManyField(User, related_name="boards_as_member")


class Task(models.Model):
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name='board')
    title = models.CharField(max_length=63)
    description = models.CharField(max_length=127)
    
    class Status(models.TextChoices):
        TODO = 'to-do', 'To Do'
        IN_PROGRESS = 'in-progress', 'In Progress'
        REVIEW = 'review', 'In Review'
        DONE = 'done', 'Done'

    class Priority(models.TextChoices):
        LOW = 'low', 'Low'
        MEDIUM = 'medium', 'Medium'
        HIGH = 'high', 'High'

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.TODO
    )

    priority = models.CharField(
        max_length=10,
        choices=Priority.choices,
        default=Priority.MEDIUM
    )

    assignee = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tasks_assignee'
    )

    reviewer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tasks_reviewer'
    )

    creator = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tasks_creator'
    )

    due_date = models.DateField()


class Comment(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments_creator'
    )

    content = models.CharField(max_length=255)
    created_at = models.DateField()

    task = models.ForeignKey(
        'Task',
        null=True, 
        blank=True,
        on_delete=models.CASCADE,
        related_name='comments'
    )

    def clean(self):
        if (self.board and self.task) or (not self.board and not self.task):
            raise ValidationError('A comment must be assigned to either a board or a task – not both and not neither.')
        
    
    def __str__(self):
        return f"{self.id}"
from django.db import models
from user_auth_app.models import UserAccount
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

class Board(models.Model):
    title = models.CharField(max_length=63)
    owner_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='boards_as_owner')
    members = models.ManyToManyField(User, related_name="boards_as_member")


class Task(models.Model):
    board = models.ForeignKey(Board, on_delete=models.CASCADE, blank=True, null=True, related_name='tasks')
    title = models.CharField(max_length=63)
    description = models.CharField(max_length=127)
    status = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(3)])
    priority = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(2)])
    assignee = models.ForeignKey(
        UserAccount,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tasks_assigned'
    )

    reviewer = models.ForeignKey(
        UserAccount,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tasks_reviewed'
    )
    due_date = models.DateField()


class Comment(models.Model):
    creator = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    content = models.CharField(max_length=255)
    created_at = models.DateField()

    board = models.ForeignKey(
        'Board', null=True, blank=True, on_delete=models.CASCADE, related_name='comments'
    )
    task = models.ForeignKey(
        'Task', null=True, blank=True, on_delete=models.CASCADE, related_name='comments'
    )

    def clean(self):
        if (self.board and self.task) or (not self.board and not self.task):
            raise ValidationError('A comment must be assigned to either a board or a task – not both and not neither.')
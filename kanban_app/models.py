"""
Database models for the Kanban application.

This module defines the core entities:
- Board: Represents a project board with members and an owner.
- Task: Represents a task within a board, with status, priority, and assigned users.
- Comment: Represents a comment on a task, authored by a user.

Each model enforces relationships and constraints to maintain
data integrity within the application.
"""


from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

class Board(models.Model):
    """
    Represents a project board in the Kanban application.

    A board has a title, an owner, and a set of members.
    The owner is responsible for managing the board.
    """


    title = models.CharField(max_length=63)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='boards_as_owner')
    members = models.ManyToManyField(User, related_name="boards_as_member")

    def __str__(self):
        return f"Board: {self.id}"


class Task(models.Model):
    """
    Represents a task within a board.

    A task has a title, description, status, priority,
    and can be assigned to specific users (assignee, reviewer, creator).
    """


    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=63)
    description = models.CharField(max_length=127)
    
    class Status(models.TextChoices):
        """
        Enumeration for task statuses.
        """
        TODO = 'to-do', 'To Do'
        IN_PROGRESS = 'in-progress', 'In Progress'
        REVIEW = 'review', 'In Review'
        DONE = 'done', 'Done'

    class Priority(models.TextChoices):
        """
        Enumeration for task priorities.
        """
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

    def __str__(self):
        return f"Task: {self.id}"


class Comment(models.Model):
    """
    Represents a comment made on a task.

    A comment must be linked to a task and includes an author,
    text content, and creation date.
    """


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
        if not self.task:
            raise ValidationError('A comment must be assigned to a task.')
        
    
    def __str__(self):
        return f"Comment: {self.id}"
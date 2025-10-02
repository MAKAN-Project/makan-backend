from django.db import models
from users.models import User
from engineers.models import Engineer

class Session(models.Model):
    session_id = models.AutoField(primary_key=True)
    scheduled_at = models.DateTimeField()
    meeting_link = models.CharField(max_length=255)
    status = models.CharField(max_length=45)
    sessionscol = models.CharField(max_length=45)
    eng = models.ForeignKey(Engineer, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        db_table = 'sessions'

    def __str__(self):
        return f"Session {self.session_id}"

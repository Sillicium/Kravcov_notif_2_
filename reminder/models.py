from django.db import models


class Reception(models.Model):
    patient_code = models.BigIntegerField()
    phone_number = models.CharField(max_length=20)
    name = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)
    middlename = models.CharField(max_length=100, null=True, blank=True)

    first_order_key = models.CharField(max_length=255, null=True, blank=True)
    second_order_key = models.CharField(max_length=255, null=True, blank=True)

    first_status_id = models.IntegerField(null=True, blank=True)
    second_status_id = models.IntegerField(null=True, blank=True)

    first_audio_link = models.TextField(null=True, blank=True)
    second_audio_link = models.TextField(null=True, blank=True)

    reception_code = models.BigIntegerField(unique=True)
    start_time = models.DateTimeField()
    processed_for_today = models.BooleanField(default=False)
    processed_for_tomorrow = models.BooleanField(default=False)
    calltime_for_tomorrow = models.DateTimeField(null=True, blank=True)
    calltime_for_today = models.DateTimeField(null=True, blank=True)
    upload_time = models.DateTimeField()

    is_added = models.BooleanField(default=False)

    def __str__(self):
        return f"Reception {self.reception_code} for patient {self.name} {self.lastname} ({self.patient_code}) created at {self.upload_time}"


class Call(models.Model):
    reception = models.ForeignKey(Reception, on_delete=models.CASCADE, related_name="calls")
    order_key = models.CharField(max_length=255)
    status_id = models.IntegerField(null=True, blank=True)
    audio_link = models.TextField(null=True, blank=True)
    call_type = models.CharField(max_length=10, choices=[('today', 'Сегодня'), ('tomorrow', 'Завтра')])

    def __str__(self):
        return f"Call for reception {self.reception.reception_code} with order_key {self.order_key}"


class ApiKey(models.Model):
    key = models.TextField()
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'API Key updated at {self.updated_at}'

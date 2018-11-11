from django.contrib import admin

from .models import User, XGBoostModel, Session, Probability
# Register your models here.

admin.site.register(User)
admin.site.register(XGBoostModel)
admin.site.register(Session)
admin.site.register(Probability)

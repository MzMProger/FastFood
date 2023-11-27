from bot.models import Log


class UserData:
    def __init__(self, context, update):
        self.context = context
        self.update = update

        if update.message:
            self.user = update.message.from_user
            self.query = None
        else:
            self.query = update.callback_query
            self.user = self.query.from_user
        try:
            self.log = Log.objects.get(chat_id=self.user.id)
        except Exception:
            self.log = Log(chat_id=self.user.id, messages={})
            self.log.save()

    @property
    def user_data(self):
        return self.log.messages

    def change_state(self, *args, **kwargs):
        self.log.messages.update(*args)
        self.log.save()

    def clear_state(self, state=0):
        self.log.messages = {'state': state}
        self.log.save()

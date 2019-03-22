import appdaemon.plugins.hass.hassapi as hass
import jdatetime
import datetime


class Garbage(hass.Hass):
    def initialize(self):
        time = datetime.time(0, 0, 0)
        self.run_hourly(self.check_garbage_day, time)

    def check_garbage_day(self, kwargs):
        day = jdatetime.date.today().day
        self.log('Checking garbage day')
        if day % 2 == 0:
            self.set_state('binary_sensor.garbage_day', state="YES")
            is_set = self.get_state('input_boolean.garbage_day') == 'on'
            now_time = datetime.datetime.now().time()
            is_time = now_time > datetime.time(hour=21) and now_time < datetime.time(hour=23)
            if is_set and is_time:
                self.turn_on_light()
                self.announce()
        else:
            self.set_state('binary_sensor.garbage_day', state="NO")

    def turn_on_light(self):
        self.log("Turning on neolight")
        self.call_service(
            'mqtt/publish',
            payload="255,63,0,025,3000",
            topic="/home/neolight/neolight/notification/set")

    def announce(self):
        self.log('Announcing garbage day')
        self.call_service(
            'tts/google_say',
            entity_id='media_player.google_home',
            message='Garbage day!')

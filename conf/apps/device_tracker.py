import appdaemon.plugins.hass.hassapi as hass
import datetime


class DeviceTracker(hass.Hass):

    def initialize(self):
        self.listen_state(self.being_home,
                          'device_tracker.galaxys9')
        self.listen_state(self.being_home,
                          'device_tracker.nexus')

    def being_home(self, entity, attribute, old, new, kwargs):
        if new == old:
            return
        lights = self.get_app("lights")
        mode = self.get_app("mode")
        sound = self.get_app("sound")

        self.log("Self: " + entity + " is " + new)

        if entity == 'device_tracker.nexus':
            partner_entity = 'device_tracker.galaxys9'
            entity_name = "Sam'meem"
        elif entity == 'device_tracker.galaxys9':
            partner_entity = 'device_tracker.nexus'
            entity_name = "Ra'ffee"

        partner_state = self.get_state(partner_entity)

        self.log("P: " + partner_entity + " is " + partner_state)

        if new == 'home' and old == 'not_home' and partner_state == 'not_home':
            mode.set_mode("Normal")
            sound.say("Welcome Home {}".format(entity_name))
            if self.now_is_between("sunset", "sunrise"):
                lights.light("doorway", "on")
                lights.light("right_side", "on")
                lights.light("main", "on")

        if new == 'not_home' and partner_state == 'not_home':
            mode.set_mode("Not home")

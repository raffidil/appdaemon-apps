import appdaemon.plugins.hass.hassapi as hass
import datetime


class TvMode(hass.Hass):
    tv_mode_last_played = "none"
    previous_type = "idle"

    def initialize(self):
        self.listen_state(self.on_kodi_change, "media_player.kodi")
        self.listen_state(self.on_android_tv_change, "media_player.android_tv")

    def on_android_tv_change(self, entity, attribute, old, new, kwargs):
        if new == old:
            return
        # mode = self.get_app("mode")
        lights = self.get_app("lights")
        androidtv = self.get_app("androidtv")

        # current_mode = mode.get_mode()
        app_id = androidtv.get_current_app_id()
        androidtv_available = androidtv.is_available()

        if androidtv_available:
            if new == 'playing' and old != new and app_id != "org.xbmc.kodi":
                lights.neolight_effect("jackcandle")
            if new != "playing" and app_id != "org.xbmc.kodi":
                lights.neolight_color(0, 0, 0)

    def on_kodi_change(self, entity, attribute, old, new, kwargs):
        if new == old:
            return
        self.log("kodiOnChange new={}, old={}".format(str(new), str(old)))
        mode = self.get_app("mode")
        sound = self.get_app("sound")
        lights = self.get_app("lights")
        kodi = self.get_app("kodi")

        current_mode = mode.get_mode()
        media_title = kodi.get_media_title()
        media_series_title = kodi.get_media_series_title()
        media_episode = str(kodi.get_media_episode())
        media_content_type = kodi.get_media_content_type()

        if media_content_type != self.previous_type and media_content_type != None:
            self.previous_type = media_content_type

        if current_mode == "TV":
            self.log("enter tv mode IF")

            if media_content_type == "tvshow" or media_content_type == "movie":
                # play tvshow and movie after idle
                if new == "playing" and old == 'idle':
                    self.log("idle to playing")
                    self.tv_mode_last_played = media_content_type
                    lights.turn_off_all_lights()
                    if media_content_type == "movie":
                        sound.say('playing {}. Enjoy!'.format(media_title))
                    if media_content_type == "tvshow":
                        sound.say('playing {}, episode {}.{}. Enjoy!'.format(
                            media_series_title, media_episode, media_title))
                        if self.now_is_between("sunset", "sunrise"):
                            lights.light("doorway", "on")

                elif old == 'paused' and new == 'playing' and self.now_is_between("sunset", "sunrise"):
                    lights.light("under_cabinet", "off")
                elif old == 'playing' and new == 'paused' and self.now_is_between("sunset", "sunrise"):
                    lights.light("under_cabinet", "on")

            # turn on undercabinet on stop (tvshow and movie)
            if old == 'playing' and new == "idle" and self.previous_type != 'music' and self.now_is_between("sunset", "sunrise"):
                lights.light("under_cabinet", "on")

        # turn off neolight on stop and pause kodi music
        if old == 'playing' and new != "playing" and self.previous_type == 'music':
            lights.neolight_color(0, 0, 0)

        # turn neolight effect to jackcandle, on kodi music play
        if new == 'playing' and media_content_type == "music":
            lights.neolight_effect("jackcandle")

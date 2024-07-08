""" 
# SileroTTS plugin 

Plugin for TTS offline

Needs to install numpy version < 2.0, torch 

"""
import os
import torch
import hashlib
from app.core.main.BasePlugin import BasePlugin
from plugins.SileroTTS.forms.SettingForms import SettingsForm
from app.core.lib.common import playSound
from app.core.lib.cache import  findInCache, copyToCache, getCacheDir

class SileroTTS(BasePlugin):

    def __init__(self,app):
        super().__init__(app,__name__)
        self.title = "SileroTTS"
        self.description = """This is a plugin get voice offline by text"""
        self.category = "App"
        self.version = "0.1"
        self.actions = ["say"]

    def initialization(self):
        pass
    
    def admin(self, request):
        settings = SettingsForm()
        if request.method == 'GET':
            settings.sample_rate.data = self.config.get('sample_rate',24000)
            settings.speaker.data = self.config.get("speaker",'xenia')
            settings.put_accent.data = self.config.get("put_accent", 1)
            settings.put_yo.data = self.config.get("put_yo", 1)
        else:
            if settings.validate_on_submit():
                self.config["sample_rate"] = settings.sample_rate.data
                self.config["speaker"] = settings.speaker.data
                self.config["put_accent"] = settings.put_accent.data
                self.config["put_yo"] = settings.put_yo.data
                self.saveConfig()
        content = {
            "form": settings,
        }
        return self.render('main_stts.html', content)
    
    def say(self, message, level=0, image: str = None, destination=None):
        
        hash = hashlib.md5(message.encode('utf-8')).hexdigest()

        # файл с кешированным аудио
        file_name = hash+'_silero.wav'

        cached_file_name = findInCache(file_name,self.name,True)
        # Проверяем, существует ли файл с кешированным аудио и не является ли он пустым
        if not cached_file_name or os.path.getsize(cached_file_name) == 0:
            sample_rate = int(self.config.get("sample_rate", 24000)) #`sample_rate` should be in [8000, 24000, 48000]
            speaker = self.config.get("speaker",'xenia') #`speaker` should be in aidar, baya, kseniya, xenia, eugene, random
            put_accent = int(self.config.get("put_accent",1)) # автоударение
            put_yo = int(self.config.get("put_yo",1))     # ё

            device = torch.device('cpu')
            torch.set_num_threads(4)
            local_file = os.path.join(getCacheDir(),self.name,'model','model.pt')
            os.makedirs(os.path.dirname(local_file), exist_ok=True)
            # скачивается в первый раз
            if not os.path.isfile(local_file):
                torch.hub.download_url_to_file('https://models.silero.ai/models/tts/ru/v4_ru.pt',local_file)  
            model = torch.package.PackageImporter(local_file).load_pickle("tts_models", "model")
            model.to(device)    
    
            audio_path = model.save_wav(text=message,
                             speaker=speaker,
                             put_accent=put_accent,
                             put_yo=put_yo,
                             sample_rate=sample_rate)

            copyToCache(audio_path,file_name,self.name + "/TTS",False)
            os.unlink(audio_path)
            cached_file_name = findInCache(file_name,self.name,True)
            self.logger.info("Файл в кэше {}.".format(cached_file_name))
        # Если файл существует и не является пустым, обрабатываем его
        if cached_file_name and os.path.getsize(cached_file_name):
            playSound(cached_file_name, level)
            
                

        
        
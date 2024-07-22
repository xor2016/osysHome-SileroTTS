from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired

# Определение класса формы
class SettingsForm(FlaskForm):
    sample_rate = SelectField('Дискретизация', validators=[DataRequired()], choices=[8000,24000,48000])
    speaker = SelectField('Диктор', validators=[DataRequired()],choices=['aidar', 'baya', 'kseniya', 'xenia', 'eugene', 'random'])
    put_accent = SelectField('Автоударение', validators=[DataRequired()], choices=[0,1])
    put_yo = SelectField('Обработка Ё', validators=[DataRequired()], choices=[0,1])
    auto_num2word = SelectField('Автоперевод чисел в текст', validators=[DataRequired()], choices=[0,1])
    propertyMinLevel = StringField('Объект.Свойство, где устанавливается мин. уровень сообщений (например, SystemVar.minMsgLevel)')
    beep_file = StringField('Звук, проигрываемый перед фразой - путь к файлу')
    submit = SubmitField('Submit')
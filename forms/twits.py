from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SubmitField
from wtforms.validators import DataRequired


class TwitsForm(FlaskForm):
    title = StringField('Название твита', validators=[DataRequired()])
    content = TextAreaField("Содержание")
    is_private = BooleanField("Скрытый")
    submit = SubmitField('Выложить')

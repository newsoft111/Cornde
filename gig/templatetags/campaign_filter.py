from datetime import datetime, timedelta
from django import template

register = template.Library()

@register.filter
def plus_days(value, days):
	return value + timedelta(days=days)


@register.filter
def make_list(value):
	return value.split(',')


@register.filter(name='check_new')
def check_new(date):
	delta = datetime.date(date) - datetime.now().date()
	delta = delta.days
	if delta > -2:
		is_new = delta
	else:
		is_new = None
	return is_new


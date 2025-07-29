#encoding:utf-8

def decorate(func):
	def Except_Error(*args):
		try:
			return func(*args)
		except Exception as e:
			print(e)
	return Except_Error

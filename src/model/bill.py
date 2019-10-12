import datetime
from enum import Enum
import unidecode

class Bill:

	def __init__(self, name, value, due_date, paid_date, payer, category="Outros", ps=""):
		self._value = None
		self._due_date = None
		self._paid_date = None
		self._payer = None

		self.name = name
		self.value = value
		self.due_date = due_date
		self.paid_date = paid_date
		self.payer = payer
		self.category = category
		self.ps = ps

	@property
	def value(self):
		return self._value
	
	@value.setter
	def value(self, value):
		self._value = "{0:.2f}".format(float(value))

	@property
	def due_date(self):
		return self._due_date
	
	@due_date.setter
	def due_date(self, value):
		if isinstance(value, datetime.datetime):
			self._due_date = value
		else:
		    datetime_object = datetime.datetime.strptime(value.lstrip().rstrip(), "%d/%m/%Y")
		    self._due_date = datetime_object.strftime("%Y-%m-%d")

	@property
	def paid_date(self):
		return self._paid_date
	
	@paid_date.setter
	def paid_date(self, value):
		if isinstance(value, datetime.datetime) or (value is None):
		    self._paid_date = value
		else:
		    datetime_object = datetime.datetime.strptime(value.lstrip().rstrip(), "%d/%m/%Y")
		    self._paid_date = datetime_object.strftime("%Y-%m-%d")

	@property
	def payer(self):
		return self._payer
	
	@payer.setter
	def payer(self, value):
		self._payer = unidecode.unidecode(value)

	def to_text(self):
		return f'conta: {self.name}\nvalor: {self.value}\ndata de vencimento: {self._format_date(self.due_date)}\ndata de pagamento: {self._format_date(self.paid_date)}\npagador: {self.payer}'

	def _format_date(self, date):
		if date:
		    return datetime.datetime.strftime(date, "%d/%m/%Y")
		else:
		    return "???"

class EFields(Enum):
	name = "conta"
	value = "valor"
	due_date = "data de vencimento"
	paid_date = "data de pagamento"
	payer = "pagador"

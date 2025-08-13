# Скрипт для анализа денежных потоков произвольной формы
##########################################################################
##########################################################################
# Импорт библиотек:
import csv, datetime, numpy
##########################################################################
##########################################################################
# Объект денежного потока:
class CashFlow:
    ######################################################################
    # Инициализация:
    def __init__(self):
        # Чтение файла ввода:
        with open('Транзакции.csv', 'r', encoding='utf-8') as file:
            reader = csv.reader(file, delimiter=' ')
            dates = list()
            sums = list()
            key = False
            self.min_value = 1000000000000
            for row in reader:
                if key:
                    dates.append(datetime.datetime.strptime(row[0],"%d.%m.%Y"))
                    value = float(row[1])
                    sums.append(value)
                    if self.min_value > abs(value):
                        self.min_value = abs(value)
                else:
                    key = True
        # Конвертация дат в номера:
        self.min_date = min(dates)
        self.max_date = max(dates)
        self.duration = (self.max_date-self.min_date).days
        days = list()
        for date in dates:
            days.append((date-self.min_date).days)
        # Избавление от повторов:
        self.values = numpy.empty(0, dtype = float)
        for number in range(1+self.duration):
            value = 0
            for day in range(len(days)):
                if days[day] == number:
                    value += sums[day]
            self.values = numpy.append(self.values, value)
    ######################################################################
    def print_dates(self):
        print(f'Начало: {self.min_date.strftime("%d.%m.%Y")};')
        print(f'Конец: {self.max_date.strftime("%d.%m.%Y")};')
        print(f'Дюрация: {format(self.duration/365.25,".2f")} лет |'\
              f' {format(self.duration*12/365.25,".2f")} месяцев |'
              f' {self.duration} дней.')
    ######################################################################
    def print_balance(self):
        d_in = -numpy.sum(self.values, where=self.values<0)
        d_out = numpy.sum(self.values, where=self.values>0)
        print(f'Расходы: {format(d_in,".2f")}₽;')
        print(f'Доходы: {format(d_out,".2f")}₽;')
        print(f'Прибыль: {format(d_out-d_in,".2f")}₽;')
        print(f'Рентабильность: {format(((d_out/d_in)**(365.25/self.duration)-1)*100,".2f")}% годовых;')
    ######################################################################
    def print_geometric(self, i):
        values = numpy.empty(len(self.values), dtype = float)
        for n in range(len(self.values)):
            values[n] = self.values[n]*(1+i)**(-n/365.25)
        d_in = -numpy.sum(values, where=values<0)
        d_out = numpy.sum(values, where=values>0)
        print(f'Ставка дисконтирования: {format(100*i,".2f")}% годовых;')
        print(f'Расходы: {format(d_in,".2f")}₽;')
        print(f'Доходы: {format(d_out,".2f")}₽;')
        print(f'Прибыль: {format(d_out-d_in,".2f")}₽;')
        print(f'Рентабильность: {format(((d_out/d_in)**(365.25/self.duration)-1)*100,".2f")}% годовых;')
    ######################################################################
    def print_irr(self):
        roots = numpy.roots(self.values[::-1])
        real_roots = roots.real[abs(roots.imag)<1e-5]
        positive_roots = real_roots[real_roots>0]
        irrs = numpy.power(positive_roots,-365.25)-1
        if len(irrs) != 1:
            print('IRR неопределена!')
        else:
            print(f'IRR: {format(irrs[0]*100,".2f")}%/год.')
    ######################################################################
    def print_nalog(self, x):
        minus = 0
        plus = 0
        for k in self.values:
            if k < 0:
                minus += 1
            elif k > 0:
                plus += 1
        if (minus != 1) or (plus == 0):
            raise(BaseException('Неправильная структура потока!'))
        values = self.values*(1-x/100)
        values[0] = self.values[0]
        l = len(self.values)-1
        values[l] = -self.values[0]+(self.values[l]+self.values[0])*(1-x/100.)
        min_value = 0.1*self.min_value*(1-x/100.)
        print('')
        for k in range(l+1):
            if abs(values[k]) > min_value:
                print(f'{(self.min_date+datetime.timedelta(k)).strftime("%d.%m.%Y")}'\
                      f' {format(values[k],".2f")}')
##########################################################################
##########################################################################
if __name__ == '__main__':
    ######################################################################
    input_string = input('Введите "h", если забыли синтаксис: ')
    if 'h' in input_string:
        print('h -- выводит настоящую справку,')
        print('d -- вычислят продолжительность потока,')
        print('b -- выисляет баланс потока,')
        print('irr -- вычисляет IRR,')
        print('is x -- вычисляет рентабильность при ставке дисконтирования x% годовых,')
        print('nalog x -- для акций: сокращает "сырой" денежный поток'\
              ' на величину подоходного налога со ставкой x% без ЛДВ')
    if 'd' in input_string:
        flow = CashFlow()
        flow.print_dates()
    if 'b' in input_string:
        flow = CashFlow()
        flow.print_balance()
    if 'irr' in input_string:
        flow = CashFlow()
        flow.print_irr()
    if 'is' in input_string:
        _, x = input_string.split(' ')
        flow = CashFlow()
        flow.print_geometric(float(x)/100.)
    if 'nalog' in input_string:
        _, x = input_string.split(' ')
        flow = CashFlow()
        flow.print_nalog(float(x))

class AtmosphericData(object):
    def __init__(self, dry_temperature: float, pressure: float, humidity: float):
        self.pressure = pressure
        self.dry_temperature = dry_temperature
        self.humidity = humidity

    def __str__(self):
        return f'Temperatur: {self.dry_temperature:.2f}, Luftdruck: {self.pressure:.2f}, Luftfeuchte: {self.humidity:.2f}'

    def wet_temperature(self):
        return 0.058 * self.humidity + 0.697 * self.dry_temperature + 0.003 * self.dry_temperature * self.humidity - 5.809

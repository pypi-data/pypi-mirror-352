class AtmosphericCorrectionData(object):
    def __init__(self, lambda_value: float, pressure: float, dry_temperature: float, wet_temperature: float):
        self.lambda_value = lambda_value
        self.pressure = pressure
        self.dry_temperature = dry_temperature
        self.wet_temperature = wet_temperature

    def __str__(self):
        return f"{self.lambda_value},{self.pressure},{self.dry_temperature},{self.wet_temperature}"

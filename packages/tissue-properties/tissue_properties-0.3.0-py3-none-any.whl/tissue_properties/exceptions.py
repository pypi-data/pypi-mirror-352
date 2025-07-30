class UndefinedProperty(RuntimeError):
    def __init__(self, property_name: str, argument_name: str):
        super().__init__(
            f"Property ({property_name}) is not defined for argument ({argument_name}). I.e. the argument is outside the valid range for the property in this dataset."
        )

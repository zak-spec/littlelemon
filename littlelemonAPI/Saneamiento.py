import bleach

class BleachCleanMixin:
    def clean_attrs(self, attrs):
        for key, value in attrs.items():
            if isinstance(value, str):
                attrs[key] = bleach.clean(value)
        return attrs

    def validate(self, attrs):
        cleaned_attrs = self.clean_attrs(attrs)
        return super().validate(cleaned_attrs)

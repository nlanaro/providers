from tastypie.validation import Validation
import pycountry


VALID_CURRENCIES = map(lambda x: x.letter, list(pycountry.currencies))
VALID_LANGUAGES = map(lambda x: x.iso639_1_code, filter(lambda x: getattr(x, 'iso639_1_code', False), list(pycountry.languages)))


class ProviderValidator(Validation):
    def is_valid(self, bundle, request=None):
        errors = {}

        for key, value in bundle.data.items():
            if not value:
                errors[key] = ['A {} is necessary'.format(key)]

            if key == 'currency' and value and value not in VALID_CURRENCIES:
                errors[key] = ['Invalid currency']

            if key == 'language' and value and value not in VALID_LANGUAGES:
                errors[key] = ['Invalid langauge']

        return errors


class ServiceAreaValidator(Validation):
    def is_valid(self, bundle, request=None):
        errors = {}

        for key, value in bundle.data.items():
            if not value:
                errors[key] = ['A {} is necessary'.format(key)]

        return errors

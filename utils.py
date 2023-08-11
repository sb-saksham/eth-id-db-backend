import random
import string


def random_string_generator(size=10, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def unique_key(instance):
    """
    :param instance:The instance of class
    :return: key created
    """
    size = random.randint(25, 30)
    key = random_string_generator(size)
    Klass = instance.__class__  # it allows you to set 'Klass' to the actual class of any instance
    qs_exists = Klass.objects.filter(key=key).exists()
    if qs_exists:
        return unique_key(instance)
    return key

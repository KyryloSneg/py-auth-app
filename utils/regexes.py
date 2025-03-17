# no support for the other alphabets because windows is the best operating system ever made (broken support for unicode-escape)
NAME_REGEX = r"[a-zA-Z\']{1,1000}"
PHONE_REGEX = r"\+{0,1}[0-9]{3,20}"
# the next ones apply only on submit:
EMAIL_REGEX = r"[^\s@]+@[^\s@]+\.[^\s@]+"
PASSWORD_REGEX = r"(([0-9]{2,})([a-z]+)([A-Z]+([!-\/:-@[-`{-~]+)).{8,512})"
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import QRegExp, Qt, QThread, pyqtSignal, QObject
from PyQt5.QtGui import QRegExpValidator, QCursor, QFont
from ui.ui import Ui_MainWindow

# utils
from utils.set_layout_visibility import hide_layout, show_layout
from utils.shown_window_enum import ShownWindowEnum
from utils.auth_options_enum import AuthOption
from utils.form_line_edits_enum import FormLineEdit
from utils.is_phone_number_valid import is_phone_number_valid

import utils.consts as consts
import utils.regexes as regexes

from services.authentication import register, login
from services.send_account_activation_message import send_account_activation_message
from services.account_activation import activate_account

import re, time
from random import randint


# using worker instead of threading / multiprocessing from python lib because the ones are not working properly in pyqt
# (at least in my case)
class SendActivationEmailTimeoutWorker(QObject):
    finished = pyqtSignal()
    
    def __init__(self, main_widget):
        super().__init__()
        self.main_widget = main_widget

    def run(self):
        while self.main_widget.send_activation_email_btn_timeout > 0 and not self.main_widget.user["isActivated"]:
            self.main_widget.render_send_activation_email_btn()
            time.sleep(1)
            self.main_widget.send_activation_email_btn_timeout -= 1
            
        self.main_widget.send_activation_email_btn_timeout = None
        self.main_widget.render_send_activation_email_btn()

        self.finished.emit()


class MainWidget(QMainWindow):
    def __init__(self):
        super().__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.welcome_label.setFont(QFont("Montserrat-Bold", 15))
        
        self.shown_window = ShownWindowEnum.form.value
        
        self.hide_activation_code_lineedit_layout()
        self.hide_profile()
        
        # some utilities related to widgets that i can't place in the consts.py file
        
        self.ALL_BOTTOM_OPTION_BTNS = [self.ui.registration_btn, self.ui.phone_signin_btn, self.ui.email_signin_btn]
        
        # binding lineedits to the corresponding enum representation
        
        self.FORM_LINEEDITS_OBJ = {}
        self.FORM_LINEEDITS_OBJ[FormLineEdit.first_name.value] = self.ui.name_lineedit
        self.FORM_LINEEDITS_OBJ[FormLineEdit.surname.value] = self.ui.surname_lineedit
        self.FORM_LINEEDITS_OBJ[FormLineEdit.phone.value] = self.ui.phone_lineedit
        self.FORM_LINEEDITS_OBJ[FormLineEdit.email.value] = self.ui.email_lineedit
        self.FORM_LINEEDITS_OBJ[FormLineEdit.password.value] = self.ui.password_lineedit
        
        # binding lineedit errors to the corresponding enum representation
        
        self.FORM_LINEEDIT_ERRORS_OBJ = {}
        self.FORM_LINEEDIT_ERRORS_OBJ[FormLineEdit.first_name.value] = self.ui.name_error_label
        self.FORM_LINEEDIT_ERRORS_OBJ[FormLineEdit.surname.value] = self.ui.surname_error_label
        self.FORM_LINEEDIT_ERRORS_OBJ[FormLineEdit.phone.value] = self.ui.phone_error_label
        self.FORM_LINEEDIT_ERRORS_OBJ[FormLineEdit.email.value] = self.ui.email_error_label
        self.FORM_LINEEDIT_ERRORS_OBJ[FormLineEdit.password.value] = self.ui.password_error_label
        
        # binding form lineedit layouts to the corresponding lineedits
        
        self.FORM_LINEEDIT_LAYOUTS_TO_LINEEDIT_OBJ = {}
        self.FORM_LINEEDIT_LAYOUTS_TO_LINEEDIT_OBJ[self.ui.name_layout] = self.ui.name_lineedit
        self.FORM_LINEEDIT_LAYOUTS_TO_LINEEDIT_OBJ[self.ui.surname_layout] = self.ui.surname_lineedit
        self.FORM_LINEEDIT_LAYOUTS_TO_LINEEDIT_OBJ[self.ui.phone_layout] = self.ui.phone_lineedit
        self.FORM_LINEEDIT_LAYOUTS_TO_LINEEDIT_OBJ[self.ui.email_layout] = self.ui.email_lineedit
        self.FORM_LINEEDIT_LAYOUTS_TO_LINEEDIT_OBJ[self.ui.password_layout] = self.ui.password_lineedit
        
        self.ALL_LINEEDIT_LAYOUTS = self.FORM_LINEEDIT_LAYOUTS_TO_LINEEDIT_OBJ.keys()
        
        # binding bottom option btns to the corresponding auth option
        
        self.BOTTOM_OPTION_BTNS_OBJ = {}
        self.BOTTOM_OPTION_BTNS_OBJ[AuthOption.register.value] = self.ui.registration_btn
        self.BOTTOM_OPTION_BTNS_OBJ[AuthOption.phone.value] = self.ui.phone_signin_btn
        self.BOTTOM_OPTION_BTNS_OBJ[AuthOption.email.value] = self.ui.email_signin_btn
        
        # binding different lineedit combinations to the corresponding auth option
        
        self.FORM_LINEEDITS_VARIANTS = {}
        self.FORM_LINEEDITS_VARIANTS[AuthOption.register.value] = self.ALL_LINEEDIT_LAYOUTS
        self.FORM_LINEEDITS_VARIANTS[AuthOption.phone.value] = [self.ui.phone_layout, self.ui.password_layout]
        self.FORM_LINEEDITS_VARIANTS[AuthOption.email.value] = [self.ui.email_layout, self.ui.password_layout]
        
        # binding submit btn text to the corresponding auth option
        
        self.SUBMIT_BTN_TEXT_VARIANTS = {}
        self.SUBMIT_BTN_TEXT_VARIANTS[AuthOption.register.value] = "Register"
        self.SUBMIT_BTN_TEXT_VARIANTS[AuthOption.phone.value] = "Log in"
        self.SUBMIT_BTN_TEXT_VARIANTS[AuthOption.email.value] = "Log in"
        
        # form bottom btns' handlers
        self.ui.submit_btn.clicked.connect(self.on_submit_btn_click)
        self.ui.registration_btn.clicked.connect(self.on_registration_btn_click)
        self.ui.phone_signin_btn.clicked.connect(self.on_phone_signin_btn_click)
        self.ui.email_signin_btn.clicked.connect(self.on_email_signin_btn_click)
        
        # profile event handlers
        
        self.ui.activation_code_lineedit.textChanged.connect(self.activation_code_lineedit_textChanged)
        self.ui.send_activation_email_btn.clicked.connect(self.send_activation_email)
        
        # form lineedit validators
        
        name_regex = surname_regex = QRegExp(regexes.NAME_REGEX)
        phone_regex = QRegExp(regexes.PHONE_REGEX)
        email_regex = QRegExp(regexes.EMAIL_REGEX)
        
        self.name_lineedit_validator = QRegExpValidator(name_regex)
        self.surname_lineedit_validator = QRegExpValidator(surname_regex)
        # (validate phone number with the phonenumbers library on submit but basic regex is always welcome) 
        self.phone_lineedit_validator = QRegExpValidator(phone_regex) 
        # (validate these ones manually on submit)
        self.email_lineedit_validator = QRegExpValidator(email_regex)
        
        self.ui.name_lineedit.setValidator(self.name_lineedit_validator)
        self.ui.surname_lineedit.setValidator(self.surname_lineedit_validator)
        self.ui.phone_lineedit.setValidator(self.phone_lineedit_validator)
        
        # main properties
        
        self.is_auth = False
        self.user = None
        self.user_address = None
        self.acc_activation_code = None
        
        self.send_activation_email_btn_timeout = None
        self.send_activation_email_btn_timeout_thread = None
        
        self.selected_auth_option = AuthOption.register.value
        self.is_submitting_form = False
        # { [AuthOption.value]: { [FormLineEdit.value]: error_msg, ... }, ... }
        self.form_errors = {}
        
        for option in AuthOption:
            self.form_errors[option.value] = {}
        
        # { [AuthOption.value]: { [FormLineEdit.value]: lineedit, ... }, ... }
        self.preserved_lineedit_text_obj = {}
        self.preserve_curr_variant_lineedit() # define its initial values values
        
        # initial rerendering to make it look right immediately
        # IMPORTANT: (render widgets with custom "is_hidden_manually" property first)
        
        self.render_form_lineedit_errors()
        self.render_form_bottom_btns()
        
        self.render_form_lineedits_curr_variant()
        
    # helpers
    
    def is_lineedit_in_curr_variant(self, lineedit):
        for layout in self.FORM_LINEEDITS_VARIANTS[self.selected_auth_option]:
            if lineedit == self.FORM_LINEEDIT_LAYOUTS_TO_LINEEDIT_OBJ[layout]:
                return True
        
        return False
        
    # preserve lineedit text content in the instance property
    
    def preserve_curr_variant_lineedit(self):
        for lineedit_layout in self.FORM_LINEEDITS_VARIANTS[self.selected_auth_option]:
            lineedit = self.FORM_LINEEDIT_LAYOUTS_TO_LINEEDIT_OBJ[lineedit_layout]
            # find FormLineEdit.value of the lineedit
            form_lineedit_enum_value = list(filter(lambda x: x[1] == lineedit, list(self.FORM_LINEEDITS_OBJ.items())))[0]
            
            try:
                ignore = self.preserved_lineedit_text_obj[self.selected_auth_option]
            except:
                 self.preserved_lineedit_text_obj[self.selected_auth_option] = {}
                
            self.preserved_lineedit_text_obj[self.selected_auth_option][form_lineedit_enum_value] = lineedit.text()
        
    # resetting form lineedits' content and errors
    
    def reset_or_restore_form_lineedits(self):
        # reset all at first just in case
        for lineedit in self.FORM_LINEEDITS_OBJ.values():
            lineedit.setText("")
            
        for lineedit_layout in self.FORM_LINEEDITS_VARIANTS[self.selected_auth_option]:
            try:
                ignore = self.preserved_lineedit_text_obj[self.selected_auth_option]
            except:
                # we haven't preserved lineedit values of this auth option yet
                break
                 
            lineedit = self.FORM_LINEEDIT_LAYOUTS_TO_LINEEDIT_OBJ[lineedit_layout]
            form_lineedit_enum_value = list(filter(lambda x: x[1] == lineedit, list(self.FORM_LINEEDITS_OBJ.items())))[0]
                
            lineedit.setText(self.preserved_lineedit_text_obj[self.selected_auth_option][form_lineedit_enum_value])
        
        self.form_errors[self.selected_auth_option] = {}
        
    # rerendering error labels
    
    def render_form_lineedit_errors(self):
        if self.shown_window == ShownWindowEnum.form.value:
            for [name, error_label] in self.FORM_LINEEDIT_ERRORS_OBJ.items():
                lineedit = self.FORM_LINEEDITS_OBJ[name]
                
                if self.is_lineedit_in_curr_variant(lineedit):
                    error_msg = self.form_errors[self.selected_auth_option].get(name)
                    
                    if error_msg:
                        error_label.setProperty("is_hidden_manually", False)
                        error_label.setText(error_msg)
                        error_label.setHidden(False)
                    else:
                        error_label.setProperty("is_hidden_manually", True)
                        error_label.setHidden(True)
        
    # rerendering form elements after selecting an auth option
        
    def render_form_lineedits_curr_variant(self):
        if self.shown_window == ShownWindowEnum.form.value:
            for lineedit_layout in self.ALL_LINEEDIT_LAYOUTS:
                if lineedit_layout in self.FORM_LINEEDITS_VARIANTS.get(self.selected_auth_option):
                    show_layout(lineedit_layout)
                else:
                    hide_layout(lineedit_layout)
        
    def render_form_bottom_btns(self):
        if self.shown_window == ShownWindowEnum.form.value:
            for btn in self.ALL_BOTTOM_OPTION_BTNS:
                if btn == self.BOTTOM_OPTION_BTNS_OBJ.get(self.selected_auth_option):
                    btn.setProperty("is_hidden_manually", True)
                    btn.setHidden(True)
                else:
                    btn.setProperty("is_hidden_manually", False)
                    btn.setHidden(False)
                
            self.ui.submit_btn.setText(self.SUBMIT_BTN_TEXT_VARIANTS.get(self.selected_auth_option))
       
    # rerendering "send activation email" btn (usually on isActivated state or timeout changes)
         
    def render_send_activation_email_btn(self):
        if self.is_auth:            
            if self.user["isActivated"]:
                self.ui.send_activation_email_btn.setDisabled(True)
                self.ui.send_activation_email_btn.setCursor(QCursor(Qt.ArrowCursor))
                self.ui.send_activation_email_btn.setText("Account is activated")
            else: 
                if self.send_activation_email_btn_timeout:
                    self.ui.send_activation_email_btn.setDisabled(True)
                    self.ui.send_activation_email_btn.setCursor(QCursor(Qt.ArrowCursor))
                    self.ui.send_activation_email_btn.setText(f"Wait {self.send_activation_email_btn_timeout} seconds to send another one")
                else:                
                    self.ui.send_activation_email_btn.setDisabled(False)
                    self.ui.send_activation_email_btn.setCursor(QCursor(Qt.PointingHandCursor))
                    self.ui.send_activation_email_btn.setText("Send an account activation mail")
        else:
            self.ui.send_activation_email_btn.setDisabled(True)
            self.ui.send_activation_email_btn.setCursor(QCursor(Qt.ArrowCursor))
    
    # showing / hiding main parts of the app

    def show_profile(self):
        self.shown_window = ShownWindowEnum.profile.value
        
        self.ui.main_layout.setSpacing(0)
        
        self.ui.main_layout.setStretch(0, 0)
        self.ui.main_layout.setStretch(1, 1)
        
        if self.is_auth:
            # replace placeholder text with user's name and surname
            self.ui.welcome_label.setText(self.ui.welcome_label.text().replace(
                consts.PROFILE_FULLNAME_PLACEHOLDER, f"{self.user["name"]} {self.user["surname"]}"
            ))
            
            self.render_send_activation_email_btn()
            
        show_layout(self.ui.profile_layout)
        
    def hide_profile(self):
        hide_layout(self.ui.profile_layout)
      
    def show_form(self):
        self.shown_window = ShownWindowEnum.form.value
        
        self.ui.main_layout.setSpacing(16)
        
        self.ui.main_layout.setStretch(0, 0)
        self.ui.main_layout.setStretch(1, 1)
        
        show_layout(self.ui.form_layout)
        
    def hide_form(self):
        hide_layout(self.ui.form_layout)
    
    def show_activation_code_layout(self):
        self.ui.activation_code_lineedit.setText("")
        self.ui.activation_code_layout.setProperty("is_hidden_manually", False)
        
        show_layout(self.ui.activation_code_layout)
        
    def hide_activation_code_lineedit_layout(self):
        self.ui.activation_code_layout.setProperty("is_hidden_manually", True)
        hide_layout(self.ui.activation_code_layout)
        
    # selecting auth option logic
        
    def select_auth_option(self, option):
        self.preserve_curr_variant_lineedit()
        self.selected_auth_option = option
        
        self.reset_or_restore_form_lineedits()
        self.render_form_lineedit_errors()
        self.render_form_lineedits_curr_variant()
        self.render_form_bottom_btns()
        
    def on_registration_btn_click(self):
        self.select_auth_option(AuthOption.register.value)
        
    def on_phone_signin_btn_click(self):
        self.select_auth_option(AuthOption.phone.value)
        
    def on_email_signin_btn_click(self):
        self.select_auth_option(AuthOption.email.value)
        
    # validating fields logic
        
    def validate_lineedits(self):
        have_errors_updated = False
        result_is_valid = True
        
        def update_form_errors(name, error_msg, is_valid):
            nonlocal have_errors_updated, result_is_valid
            
            if is_valid:
                try:
                    # if such a field exists
                    del self.form_errors[self.selected_auth_option][name]
                    have_errors_updated = True
                except:
                    pass
            else:
                result_is_valid = False
                
                try:
                    ignore = self.form_errors[self.selected_auth_option][name]
                except:
                    # if no such a field
                    self.form_errors[self.selected_auth_option][name] = error_msg
                    have_errors_updated = True
                    
        
        # the cb must have text as its first and the only arg
        def validate_field(lineedit, custom_validator_cb, name, error_msg):
            if self.is_lineedit_in_curr_variant(lineedit):
                is_valid = custom_validator_cb(lineedit.text())
                update_form_errors(name, error_msg, is_valid)
                
        
        # getting rid of the position arg of .validate method 
        def get_custom_validator(validator):
            def custom_validator(text):
                return validator.validate(text, 0)[0] != 1
            
            return custom_validator
        
        
        def validate_phone_lineedit(phone):
            if re.search(r"\++", phone):
                phone_of_international_format = phone
            else:
                phone_of_international_format = f"+{phone}"
            
            is_validator_valid = self.phone_lineedit_validator.validate(phone, 0)[0] != 1
            is_phone_valid = is_phone_number_valid(phone_of_international_format)
            
            return is_validator_valid and is_phone_valid
        
        
        def validate_password_lineedit(password):
            password = password.strip()
            
            # python or windows doesn't like long regexes for password that work perfectly fine in js, so just validate one manually:            
            does_contain_lowercase_letter = re.search(r"[a-z]+", password)
            does_contain_uppercase_letter = re.search(r"[A-Z]+", password)
            does_contain_2_or_more_digits = re.search(r"[0-9]{2,}", password)
            does_contain_special_char = re.search(r"[!-\/:-@[-`{-~]+", password)
            is_allowed_length = consts.MIN_PASSWORD_LENGTH <= len(password) <= consts.MAX_PASSWORD_LENGTH 
            
            is_allowed_password = (
                does_contain_lowercase_letter and does_contain_uppercase_letter and does_contain_2_or_more_digits 
                and does_contain_special_char and is_allowed_length
            )
            
            is_equal_to_email = password == self.ui.email_lineedit.text().strip()
            
            return is_allowed_password and not is_equal_to_email
        
        
        validate_field(
            self.ui.name_lineedit, get_custom_validator(self.name_lineedit_validator), 
            FormLineEdit.first_name.value, consts.NAME_ERROR_MSG
        )
        
        validate_field(
            self.ui.surname_lineedit, get_custom_validator(self.surname_lineedit_validator), 
            FormLineEdit.surname.value, consts.SURNAME_ERROR_MSG
        )
        
        validate_field(
            self.ui.phone_lineedit, validate_phone_lineedit, FormLineEdit.phone.value, consts.PHONE_ERROR_MSG
        )
        
        validate_field(
            self.ui.email_lineedit, get_custom_validator(self.email_lineedit_validator), 
            FormLineEdit.email.value, consts.EMAIL_ERROR_MSG
        )
        
        validate_field(
            self.ui.password_lineedit, validate_password_lineedit, FormLineEdit.password.value, consts.PASSWORD_ERROR_MSG
        )
        
        if have_errors_updated:
            self.render_form_lineedit_errors()
            
        return result_is_valid
    
    # submitting the form logic
        
    def on_submit_btn_click(self):
        # redundant check but let it be as a reminder that submitting a form in pyqt5 + pymongo is near instant
        if not self.is_submitting_form:
            try:
                self.is_submitting_form = True
                is_valid_form = self.validate_lineedits()
                    
                if is_valid_form:
                    response = None
                    
                    try:
                        if self.selected_auth_option == AuthOption.register.value:
                            response = register(
                                self.ui.name_lineedit.text().strip(), self.ui.surname_lineedit.text().strip(),
                                self.ui.phone_lineedit.text().strip(), self.ui.email_lineedit.text().strip(), 
                                self.ui.password_lineedit.text().strip()
                            )
                        elif self.selected_auth_option == AuthOption.phone.value:
                            response = login(self.ui.phone_lineedit.text().strip(), self.ui.password_lineedit.text().strip(), "phone")
                        elif self.selected_auth_option == AuthOption.email.value:
                            response = login(self.ui.email_lineedit.text().strip(), self.ui.password_lineedit.text().strip(), "email")
                    except Exception as ex:
                        pass
                    
                    if response:
                        if response["success"]:
                            self.is_auth = True
                            
                            self.user = response["data"]["user"]
                            self.user_address = response["data"]["user_address"]
                            
                            self.hide_form()
                            self.show_profile()
                        else:
                            # show the errors about invalid email / phone / password 
                            self.form_errors[self.selected_auth_option] = response["data"]
                            self.render_form_lineedit_errors()
            finally:
                self.is_submitting_form = False
        
    # send_activation_email_btn event handler
    
    def send_activation_email(self):
        self.acc_activation_code = str(randint(100000, 999999))
        has_sent_msg_successfully = send_account_activation_message(self.user_address["email"], self.acc_activation_code)
        
        if has_sent_msg_successfully:
            # show the sent code lineedit
            self.show_activation_code_layout()
        
        # set timeout to the btn in order to not spam with mails and not explode smtp servers
        self.send_activation_email_btn_timeout = consts.SEND_ACTIVATION_EMAIL_BTN_TIMEOUT_S
        
        def set_activation_email_timeout():
            self.send_activation_email_btn_timeout_thread = QThread()
            self.send_activation_email_btn_timeout_worker = SendActivationEmailTimeoutWorker(self)
            
            self.send_activation_email_btn_timeout_worker.moveToThread(self.send_activation_email_btn_timeout_thread)
            
            self.send_activation_email_btn_timeout_thread.started.connect(self.send_activation_email_btn_timeout_worker.run)
            
            self.send_activation_email_btn_timeout_worker.finished.connect(self.send_activation_email_btn_timeout_thread.quit)
            self.send_activation_email_btn_timeout_worker.finished.connect(self.send_activation_email_btn_timeout_worker.deleteLater)
            self.send_activation_email_btn_timeout_thread.finished.connect(self.send_activation_email_btn_timeout_thread.deleteLater)
            
            self.send_activation_email_btn_timeout_thread.start()
            
        set_activation_email_timeout()
        
    # activation_code_lineedit textChanged event handler
        
    def activation_code_lineedit_textChanged(self, event):
        if self.ui.activation_code_lineedit.text().replace(" ", "") == self.acc_activation_code:
            try:  
                activate_account(self.user["_id"])
                self.user["isActivated"] = True
                
                self.hide_activation_code_lineedit_layout()
                self.render_send_activation_email_btn()
            except Exception as ex:
                print("Something went wrong while activating account", ex)

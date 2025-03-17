from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QRegExpValidator
from ui.ui import Ui_MainWindow

# utils
from utils.set_layout_visibility import hide_layout, show_layout
from utils.auth_options_enum import AuthOption
from utils.form_line_edits_enum import FormLineEdit

import utils.consts as consts
import utils.regexes as regexes


class MainWidget(QMainWindow):
    def __init__(self):
        super().__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
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
        
        # form lineedit validators
        
        name_regex = surname_regex = QRegExp(regexes.NAME_REGEX)
        phone_regex = QRegExp(regexes.PHONE_REGEX)
        email_regex = QRegExp(regexes.EMAIL_REGEX)
        password_regex = QRegExp(regexes.PASSWORD_REGEX)
        
        self.name_lineedit_validator = QRegExpValidator(name_regex)
        self.surname_lineedit_validator = QRegExpValidator(surname_regex)
        # (validate phone number with the phonenumbers library on submit but basic regex is always welcome) 
        self.phone_lineedit_validator = QRegExpValidator(phone_regex) 
        # (validate these ones manually on submit)
        self.email_lineedit_validator = QRegExpValidator(email_regex)
        self.password_lineedit_validator = QRegExpValidator(password_regex)
        
        self.ui.name_lineedit.setValidator(self.name_lineedit_validator)
        self.ui.surname_lineedit.setValidator(self.surname_lineedit_validator)
        self.ui.phone_lineedit.setValidator(self.phone_lineedit_validator)
        
        # main properties
        
        self.selected_auth_option = AuthOption.register.value
        # { [AuthOption.value]: { [FormLineEdit.value]: error_msg, ... }, ... }
        self.form_errors = {}
        
        for option in AuthOption:
            self.form_errors[option.value] = {}
        
        # { [AuthOption.value]: { [FormLineEdit.value]: lineedit, ... }, ... }
        self.preserved_lineedit_text_obj = {}
        self.preserve_curr_variant_lineedit() # define its initial values values
        
        # initial rerendering to make it look right immediately
        # (render widgets with custom "is_hidden_manually" property first)
        
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
        for [name, error_label] in self.FORM_LINEEDIT_ERRORS_OBJ.items():
            lineedit = self.FORM_LINEEDITS_OBJ[name]
            
            # print(name, self.form_errors[self.selected_auth_option].get(name), self.is_lineedit_in_curr_variant(lineedit))
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
        for lineedit_layout in self.ALL_LINEEDIT_LAYOUTS:
            if lineedit_layout in self.FORM_LINEEDITS_VARIANTS.get(self.selected_auth_option):
                show_layout(lineedit_layout)
            else:
                hide_layout(lineedit_layout)
        
    def render_form_bottom_btns(self):
        for btn in self.ALL_BOTTOM_OPTION_BTNS:
            if btn == self.BOTTOM_OPTION_BTNS_OBJ.get(self.selected_auth_option):
                btn.setProperty("is_hidden_manually", True)
                btn.setHidden(True)
            else:
                btn.setProperty("is_hidden_manually", False)
                btn.setHidden(False)
                
        self.ui.submit_btn.setText(self.SUBMIT_BTN_TEXT_VARIANTS.get(self.selected_auth_option))
    
    # showing / hiding main parts of the app

    def show_profile(self):
        # TODO: set layoutStretch property of the main layout to (1, 0)
        show_layout(self.ui.profile_layout)
        
    def hide_profile(self):
        hide_layout(self.ui.profile_layout)
      
    def show_form(self):
        # TODO: set layoutStretch property of the main layout to (0, 1)
        show_layout(self.ui.form_layout)
        
    def hide_form(self):
        hide_layout(self.ui.form_layout)
        
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
        is_valid = True
        
        print(self.form_errors[self.selected_auth_option])
        def update_form_errors(name, error_msg, is_valid):
            nonlocal have_errors_updated
            
            print(name, error_msg, is_valid)
            if is_valid:
                try:
                    # if such a field exists
                    del self.form_errors[self.selected_auth_option][name]
                    have_errors_updated = True
                    print("deleted")
                except:
                    pass
            else:
                is_valid = False
                
                try:
                    ignore = self.form_errors[self.selected_auth_option][name]
                except:
                    # if no such a field
                    self.form_errors[self.selected_auth_option][name] = error_msg
                    have_errors_updated = True
                    print("added")
                    
        
        # the cb must have text as its first and the only arg
        def validate_field(lineedit, custom_validator_cb, name, error_msg):
            if self.is_lineedit_in_curr_variant(lineedit):
                print("in curr variant")
                is_valid = custom_validator_cb(lineedit.text())
                update_form_errors(name, error_msg, is_valid)
                
        
        # getting rid of the position arg of .validate method 
        def get_custom_validator(validator):
            def custom_validator(text):
                print(text, validator.validate(text, 0))
                return validator.validate(text, 0)[0] != 1
            
            return custom_validator
        
        
        def validate_phone_lineedit(phone):
            is_validator_valid = self.phone_lineedit_validator.validate(phone, 0)[0] != 1
            is_phone_valid = True
            
            return is_validator_valid and is_phone_valid
        
        
        def validate_password_lineedit(password):
            password = password.strip()
            
            is_validator_valid = self.password_lineedit_validator.validate(password, 0)[0] != 1
            is_equal_to_email = password == self.ui.email_lineedit.text().strip()
            
            return is_validator_valid and not is_equal_to_email
        
        
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
            print("render fucking errors to fuck the user")
            self.render_form_lineedit_errors()
            
        return is_valid
    
    # submitting the form logic
        
    def on_submit_btn_click(self):
        try:
            is_valid_form = self.validate_lineedits()
            
            if is_valid_form:
                # TODO: for sign in options wait for the service response and, possibly, 
                # show the errors about invalid email / phone / password 
                pass
        except:
            pass
        
    def send_activation_email(self):
        # TODO: set some sort of a timeout and send an activation email (and show the sent code lineedit)
        pass

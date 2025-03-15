from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import QRect
from ui.ui import Ui_MainWindow

# utils
from utils.set_layout_visibility import hide_layout, show_layout
from utils.auth_options_enum import AuthOption


class MainWidget(QMainWindow):
    def __init__(self):
        super().__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        self.hide_profile()
        
        # some utilities related to widgets that i can't place in the consts.py file
        
        self.ALL_BOTTOM_OPTION_BTNS = [self.ui.registration_btn, self.ui.phone_signin_btn, self.ui.email_signin_btn]
        self.ALL_LINEEDIT_LAYOUTS = [
            self.ui.name_layout, self.ui.surname_layout, self.ui.phone_layout, 
            self.ui.email_layout, self.ui.password_layout
        ]
        
        # python why can't i just write smth like this:
        
        # self.BOTTOM_OPTION_BTNS_OBJ = {
        #     [AuthOption.register.value]: self.ui.registration_btn,
        #     [AuthOption.phone.value]: self.ui.phone_signin_btn,
        #     [AuthOption.email.value]: self.ui.email_signin_btn,
        # }
        
        self.BOTTOM_OPTION_BTNS_OBJ = {}
        self.BOTTOM_OPTION_BTNS_OBJ[AuthOption.register.value] = self.ui.registration_btn
        self.BOTTOM_OPTION_BTNS_OBJ[AuthOption.phone.value] = self.ui.phone_signin_btn
        self.BOTTOM_OPTION_BTNS_OBJ[AuthOption.email.value] = self.ui.email_signin_btn
        
        self.FORM_LINEEDITS_VARIANTS = {}
        self.FORM_LINEEDITS_VARIANTS[AuthOption.register.value] = self.ALL_LINEEDIT_LAYOUTS
        self.FORM_LINEEDITS_VARIANTS[AuthOption.phone.value] = [self.ui.phone_layout, self.ui.password_layout]
        self.FORM_LINEEDITS_VARIANTS[AuthOption.email.value] = [self.ui.email_layout, self.ui.password_layout]
        
        self.SUBMIT_BTN_TEXT_VARIANTS = {}
        self.SUBMIT_BTN_TEXT_VARIANTS[AuthOption.register.value] = "Register"
        self.SUBMIT_BTN_TEXT_VARIANTS[AuthOption.phone.value] = "Log in"
        self.SUBMIT_BTN_TEXT_VARIANTS[AuthOption.email.value] = "Log in"
        
        # form bottom btns' handlers
        self.ui.submit_btn.clicked.connect(self.on_submit_btn_click)
        self.ui.registration_btn.clicked.connect(self.on_registration_btn_click)
        self.ui.phone_signin_btn.clicked.connect(self.on_phone_signin_btn_click)
        self.ui.email_signin_btn.clicked.connect(self.on_email_signin_btn_click)
        
        self.selected_auth_option = AuthOption.register.value
        
        self.render_form_lineedits_curr_variant()
        self.render_form_bottom_btns()
        
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
                btn.setHidden(True)
            else:
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
        self.selected_auth_option = option
        
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
        return True
    
    # submitting the form logic
        
    def on_submit_btn_click(self):
        try:
            is_valid_form = self.validate_lineedits()
            
            if is_valid_form:
                pass
            else:
                pass
        except:
            pass
        
    def send_activation_email(self):
        # TODO: set some sort of a timeout and send an activation email
        pass

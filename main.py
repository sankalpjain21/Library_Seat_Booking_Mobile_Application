import datetime as dt
import json
import time
import traceback
from concurrent.futures import ThreadPoolExecutor
import requests
import os
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.lang.builder import Builder
from kivy.uix.modalview import ModalView
from kivy.uix.spinner import Spinner
from kivymd.app import MDApp
from kivymd.uix.button import MDFlatButton
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.expansionpanel import MDExpansionPanel, MDExpansionPanelOneLine
from kivymd.uix.filemanager import MDFileManager
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.list import ThreeLineListItem, ThreeLineIconListItem, IconLeftWidget,OneLineListItem,TwoLineListItem
from kivymd.uix.pickers import MDDatePicker
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager



class TimePickerDialog(ModalView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (0.5, 0.2)
        self.auto_dismiss = False

        layout = MDGridLayout(cols=1, padding=20, spacing=20)
        time_layout = MDGridLayout(cols=2, padding=10, spacing=10)

        # Time range spinner
        self.time_range_spinner = Spinner(
            text='Select Time',
            values=[f'{str(i).zfill(2)}:00-{str(i + 1).zfill(2)}:00' for i in range(9, 20)],
            size_hint_y=None,
            height=40
        )
        time_layout.add_widget(MDLabel(text='Select Time:'))
        time_layout.add_widget(self.time_range_spinner)
        layout.add_widget(time_layout)
        # OK and Cancel buttons
        button_layout = MDGridLayout(cols=2, size_hint_y=None, height=50, spacing=20)

        ok_button = MDFlatButton(text='OK', on_release=self.on_ok)
        cancel_button = MDFlatButton(text='Cancel', on_release=self.on_cancel)

        button_layout.add_widget(ok_button)
        button_layout.add_widget(cancel_button)

        layout.add_widget(button_layout)
        self.add_widget(layout)

    def on_ok(self, instance):
        selected_time_range = self.time_range_spinner.text
        self.dismiss()

        self.switch_to_hall_selection()
        if self.from_on_time_selected:
            self.from_on_time_selected((selected_time_range.split("-"))[0])
        if self.to_on_time_selected:
            self.to_on_time_selected((selected_time_range.split("-"))[1])

    def on_cancel(self,*args):
        self.switch_to_user_dashboard()
        self.dismiss()


class Home_scr(MDScreen):
    pass


class Login_scr(MDScreen):
    pass


class Upcoming_Booking(MDScreen):
    pass


class Account_setting(MDScreen):
    pass

class Help(MDScreen):
    pass


class User_Dashboard(MDScreen):
    pass


class Hall_selection(MDScreen):
    pass

class Past_booking(MDScreen):
    pass
class Payment_scr(MDScreen):
    pass


class Seat_selection1(MDScreen):
    pass

class Seat_selection2(MDScreen):
    pass

# global collection
class SeatbookerApp(MDApp):
    dialog = None
    client = None
    db = None
    collection = None
    collection1 = None
    collection2 = None
    collection3 = None
    from_selected_time = None
    to_selected_time = None
    should_auto_scroll = True
    def build(self):
        self.theme_cls.primary_palette = "Amber"
        self.theme_cls.theme_style = "Dark"
        self.executer = ThreadPoolExecutor(max_workers=6)
        self.firebase_url = 'https://libraryseatbooking-37c44-default-rtdb.firebaseio.com/'
        self.executer.submit(self.load_scrs)
        self.bldr = Builder.load_file("SeatbookerApp.kv")
        return self.bldr
    def load_scrs(self):
        sm = MDScreenManager()
        sm.add_widget(Home_scr(name="home"))
        sm.add_widget(Login_scr(name="login"))
        sm.add_widget(User_Dashboard(name="user_dashboard"))
        sm.add_widget(Upcoming_Booking(name="upcoming_Booking"))
        sm.add_widget(Hall_selection(name="hall_selection"))
        sm.add_widget(Seat_selection1(name="seat_selection1"))
        sm.add_widget(Seat_selection2(name="seat_selection2"))
        sm.add_widget(Account_setting(name="account_setting"))
        sm.add_widget(Past_booking(name="past_booking"))
        sm.add_widget(Help(name="help"))
        sm.add_widget(Payment_scr(name="payment"))

    def on_start(self):
        self.bldr.get_screen("hall_selection").ids.container.add_widget(
            OneLineListItem(
                text="UG Hall",
                on_release=lambda x: self.seatselection("UG Hall")
            )
        )
        self.bldr.get_screen("hall_selection").ids.container.add_widget(
            ThreeLineListItem(
                text="PG Hall",
                on_release=lambda i: self.seatselection("PG Hall")
            )
        )

    def on_stop(self):
        self.executer.shutdown(wait=True)

    def connect_to_firebase(self):
        self.executer.submit(self.connect_to_firebase_in_background)
    def connect_to_firebase_in_background(self):
        # time.sleep(10)
        upcoming_booking_path = "Upcoming_Booking"
        upcoming_booking_url = f"{self.firebase_url}/{upcoming_booking_path}"
        past_booking_path = "Past_booking"
        past_booking_url = f"{self.firebase_url}/{past_booking_path}"

        # List to store past booking data
        past_booking_data = []

        try:
            # Fetch upcoming bookings
            response = requests.get(f"{upcoming_booking_url}.json")
            if response.status_code == 200:
                upcoming_booking_data = response.json()

                if isinstance(upcoming_booking_data, list):
                    for booking_id_key, booking_details in enumerate(upcoming_booking_data):
                        if isinstance(booking_details, dict):
                            # Parse date and time
                            seat_date = booking_details.get("date")
                            seat_to_time = booking_details.get("to_time")
                            booked_datetime = dt.datetime.strptime(f"{seat_date} {seat_to_time}", "%d-%m-%Y %H:%M:%S")
                            current_datetime = dt.datetime.now()

                            # Check if the booking date has passed
                            if booked_datetime <= current_datetime:
                                past_booking_data.append(booking_details)
                                try:
                                    response1 = requests.delete(f"{upcoming_booking_url}/{booking_id_key}.json")
                                    if response1.status_code == 200:
                                        continue
                                except Exception as e:
                                    self.show_error_dialog(f"Error {e}")
                                hall_path1 = "hall_A_seat_details"
                                hall_url = f"{self.firebase_url}/{hall_path1}"
                                try:
                                    response = requests.get(f"{hall_url}.json")
                                    if response.status_code == 200:
                                        seat_data = response.json()
                                        if isinstance(seat_data, list):
                                            validated_seat = []
                                            # self.seat_id = None

                                            seat_id2 = None
                                            for seat_id_key, seat_details in enumerate(seat_data):
                                                if isinstance(seat_details, dict):
                                                    seat_ids = seat_details.get("seat_id")
                                                    seat_status = seat_details.get("status")
                                                    if seat_status == "Booked":
                                                        validated_seat.append(seat_id_key)
                                            if validated_seat:
                                                for i in validated_seat:
                                                    hall_A_data = json.dumps(
                                                        {"status": "available", "Booked_by": "None"})
                                                    update_response = requests.patch(f"{hall_url}/{i}.json", data=hall_A_data)
                                                    if update_response.status_code == 200:
                                                        continue
                                except Exception as e:
                                    self.show_error_dialog(f"Error {e}")
                                hall_path1 = "hall_B_seat_details"
                                hall_url = f"{self.firebase_url}/{hall_path1}"
                                try:
                                    response = requests.get(f"{hall_url}.json")
                                    if response.status_code == 200:
                                        seat_data = response.json()
                                        if isinstance(seat_data, list):
                                            validated_seat = []
                                            # self.seat_id = None

                                            seat_id2 = None
                                            for seat_id_key, seat_details in enumerate(seat_data):
                                                if isinstance(seat_details, dict):
                                                    seat_ids = seat_details.get("seat_id")
                                                    seat_status = seat_details.get("status")
                                                    if seat_status == "Booked":
                                                        validated_seat.append(seat_id_key)
                                            if validated_seat:
                                                for i in validated_seat:
                                                    hall_A_data = json.dumps(
                                                        {"status": "available", "Booked_by": "None"})
                                                    update_response = requests.patch(f"{hall_url}/{i}.json",
                                                                                     data=hall_A_data)
                                                    if update_response.status_code == 200:
                                                        continue
                                except Exception as e:
                                    self.show_error_dialog(f"Error {e}")
        except Exception as e:
            self.show_error_dialog(f"Error{e}")

        try:
            # Check for existing data in Past_booking to find the last booking number
            getting_response = requests.get(f"{past_booking_url}.json")
            if getting_response.status_code == 200:
                booking_data = getting_response.json()

                if isinstance(booking_data, dict):
                    # If booking_data is a dictionary, get the last key and increment it
                    last_number = max(int(key) for key in booking_data.keys())
                elif isinstance(booking_data, list):
                    # If booking_data is a list, set last_number based on its length
                    last_number = len(booking_data)
                else:
                    # If booking_data is None, start from 1
                    last_number = 1
            else:
                last_number = 1

            # Insert each past booking entry individually in Firebase
            try:
                for booking in past_booking_data:
                    past_response = requests.put(f"{past_booking_url}/{last_number}.json", json=booking)
                    if past_response.status_code == 200:
                        last_number += 1  # Increment for the next booking entry

            except Exception as e:
                self.show_error_dialog(e)

        except Exception as e:
            self.show_error_dialog(e)

    def get_data(self):
        self.username = self.bldr.get_screen("login").ids.username.text
        self.password = self.bldr.get_screen("login").ids.passwd.text
        self.checkuser()
    def checkuser(self):
        path = 'student_details'
        url = f'{self.firebase_url}/{path}.json'
        try:
            response = requests.get(url)
            if response.status_code == 200:
                users_data = response.json()
                if isinstance(users_data, list):
                    validated_user = None
                    for user_details in users_data:
                        if isinstance(user_details, dict):
                            username = user_details.get('USERNAME')
                            fullname = user_details.get('FULLNAME')
                            password = user_details.get('PASSWORD')
                            if username is not None and password is not None:
                                if username == self.username.upper() and password == self.password:
                                    # Set validated_user to the username and password only
                                    validated_user = {
                                        "USERNAME": username,
                                        "PASSWORD": password,
                                        "FULLNAME": fullname
                                    }
                                    break  # Exit loop when a match is found

                    # Validate user existence and print specific fields
                    if validated_user:
                        self.bldr.get_screen("user_dashboard").ids.name.text = f"Welcome {validated_user['FULLNAME']}"
                        self.bldr.get_screen("user_dashboard").ids.name1.text = f"Name: {validated_user['FULLNAME']}"
                        self.bldr.get_screen("user_dashboard").ids.header_title.text = validated_user['FULLNAME']
                        self.switch_to_user_dashboard()
                    else:
                        self.show_error_dialog("Please check your username or password")

                else:
                    self.show_error_dialog("User does not exist")

            else:
                self.show_error_dialog(f"Error: {response.status_code}, {response.text}")
        except Exception as e:
            self.show_error_dialog(f"Failed to Connect because : {e}")
    def select_path(self, path):
        # When a file is selected, update the image source
        self.bldr.get_screen("user_dashboard").ids.header_image.source = path
        self.file_manager.close()
        # self.dialog.dismiss()

    def hello_print(self):
        self.file_manager = MDFileManager(
            select_path=self.select_path,  # Function to handle file selection
            ext=[".png", ".jpg", ".jpeg"],  # Filter for supported image types
            preview=True
        )
        self.file_manager.show("Device storage/DCIM/")


    def check_and_update(self):
        old_paaswd = self.bldr.get_screen("account_setting").ids.old_passwd.text
        new_paaswd = self.bldr.get_screen("account_setting").ids.new_passwd.text
        confirm_paaswd = self.bldr.get_screen("account_setting").ids.con_passwd.text
        path = 'student_details'
        url = f'{self.firebase_url}/{path}.json'
        try:
            response = requests.get(url)
            if response.status_code == 200:
                users_data = response.json()
                if isinstance(users_data, list):
                    validated_user = None
                    user_id = None
                    for user_id_key, user_details in enumerate(users_data):
                        if isinstance(user_details, dict):
                            username = user_details.get('USERNAME')
                            password = user_details.get('PASSWORD')
                            if username is not None and password is not None:
                                if str(username).upper() == str(self.username).upper() and str(password) == str(old_paaswd):
                                    validated_user = {
                                        "USERNAME": username,
                                        "PASSWORD": password
                                    }
                                    user_id = user_id_key  # Store user_id for updating password
                                    break
                    if validated_user and user_id:
                        update_url = f"{self.firebase_url}/student_details/{user_id}.json"
                        if new_paaswd == confirm_paaswd:
                            update_data = json.dumps({"PASSWORD": confirm_paaswd})
                            update_response = requests.patch(update_url, data=update_data)
                            if update_response.status_code == 200:
                                self.show_error_dialog("Successfully, Password Changed")
                            else:
                                self.show_error_dialog(
                                    f"Failed to update password: {response.status_code}, {response.text}")
        except Exception as e:
            self.show_error_dialog(f"Error,{e}")

    def switch_to_home(self):
        self.root.current = "home"

    def switch_to_login(self):
        self.username = self.bldr.get_screen("login").ids.username.text = ""
        self.password = self.bldr.get_screen("login").ids.passwd.text = ""
        self.root.current = "login"

    def switch_to_user_dashboard(self):
        self.root.current = "user_dashboard"

    def switch_to_hall_selection(self):
        self.root.current = "hall_selection"

    def switch_to_Account_setting(self):
        self.root.current = "account_setting"

    def switch_to_help(self):
        self.root.current = "help"

    def switch_to_seat_selection1(self):
        self.root.current = "seat_selection1"

    def switch_to_seat_selection2(self):
        self.root.current = "seat_selection2"

    def on_pre_enter_on_help(self):
        self.initial_questions = [
            {"text":"Book Seat","pos_hint":{"center_x":0.13,"center_y":0.82}},
            {"text":"What are the library’s opening and closing times?","pos_hint":{"center_x":0.38,"center_y":0.75}},
            {"text":"How do I reserve a seat in the library?","pos_hint":{"center_x":0.3,"center_y":0.68}},
            {"text":"How can I cancel my seat booking?","pos_hint":{"center_x":0.3,"center_y":0.61}},
            {"text":"More","pos_hint":{"center_x":0.45,"center_y":0.82}},
            {"text":"Contact Support","pos_hint":{"center_x":0.2,"center_y":0.54}}
        ]
        self.additional_questions = [
            {"text":"How do I check my current bookings?","pos_hint":{"center_x":0.32,"center_y":0.82}},
            {"text":"What are the library rules regarding food, drinks, and noise?","pos_hint":{"center_x":0.45,"center_y":0.75}},
            {"text":"Are there penalties for missing or canceling a booking late?","pos_hint":{"center_x":0.46,"center_y":0.68}},
            {"text":"What should I do if I’m unable to book a seat online?","pos_hint":{'center_x':0.4,"center_y":0.61}},
            {"text":"Less","pos_hint":{"center_x":0.65,"center_y":0.82}},
            {"text":"Contact Support","pos_hint":{"center_x":0.2,"center_y":0.54}}
        ]
        self.add_button_help(self.initial_questions)
    def add_button_help(self,questions):
        button_box = self.bldr.get_screen("help").ids.help_questions
        button_box.clear_widgets()

        for question in questions:
            btn = MDRaisedButton(
                text=question["text"],
                pos_hint=question["pos_hint"],
                on_release=lambda btn: self.handle_button(btn.text)
            )
            button_box.add_widget(btn)
    def handle_button(self, question):
        support_field = self.bldr.get_screen("help").ids.support_field
        support_button = self.bldr.get_screen("help").ids.support_button
        if question == "More":
            self.add_button_help(self.additional_questions)
        elif question == "Book Seat":
            self.book_seat()
        elif question == "Less":
            self.add_button_help(self.initial_questions)
        elif question == "Contact Support":
            self.add_message("Please type your problem below in the textfield",from_user=False)
            support_field.visible = True
            support_button.visible = True
            support_field.opacity = 1
            support_button.opacity = 1
            support_field.focus = True
        else:
            support_field.visible = False
            support_button.visible = False
            support_field.opacity = 0
            support_button.opacity = 0
            self.add_message(question, from_user=True)
            response_text = self.get_predefined_response(question)
            Clock.schedule_once(lambda dt: self.add_message(response_text, from_user=False), 0.5)
    def add_message(self, text, from_user=True):
        messages_box = self.bldr.get_screen("help").ids.messages_box
        message_label = MDLabel(
            text=text,
            halign="right" if from_user else "left",
            theme_text_color="Primary",
            size_hint_y=None,
            font_style="Body1",
        )
        message_label.height = "30dp"
        messages_box.add_widget(message_label)
    def get_predefined_response(self,questions):
        responses = {
            "Book Seat": "Going to Seat Book",
            "What are the library’s opening and closing times?": "Opening time is 9:00 AM and closing time is 08:00 PM",
            "How do I reserve a seat in the library?": "To reserve a seat, Click on Book Seat!",
            "How can I cancel my seat booking?": "Yes, you can cancel your booking by navigating the Upcoming Bookings if available from User Dashboard.",
            "How do I check my current bookings?": "Yes,you can check your booking by navigating the Upcoming Bookings if available from User Dashboard .",
            "What are the library rules regarding food, drinks, and noise?": "You need to maintain the the decorumof the libarary and also you neither eat food nor drink anything inside the library.",
            "Are there penalties for missing or canceling a booking late?": "Yes, there is a penalty for missing the booking but you can easily cancel the upcoming booking without any penalty.",
            "What should I do if I’m unable to book a seat online?": "Please click on Contact Support or You can also vist the library as well."
        }
        return responses.get(questions, "I'm here to help with your library queries!")

    def handle_contact_support(self):
        support_field = self.bldr.get_screen("help").ids.support_field.text
        if len(str(support_field)) != 0:
            self.add_message(str(support_field),from_user=True)
            path="Contact_support"
            url = f"{self.firebase_url}/{path}"
            try:
                response = requests.get(f"{url}.json")
                if response.status_code == 200:
                    response_data = response.json()
                    reponse_id = []
                    if response_data is not None:
                        for id1, details in enumerate(response_data):
                            reponse_id.append(id1)
                        next_id = max(reponse_id) + 1
                    else:
                        next_id = 1
                    query_data = {
                        "USERNAME": self.username,
                        "QUERY" : str(support_field)
                    }
                    try:
                        reponse1 = requests.patch(f"{url}/{next_id}.json",json=query_data)
                        if reponse1.status_code == 200:
                            self.add_message("The Problem and been reached to library admin, Please wait the problem will be solved as soon as possible.",from_user=False)
                    except Exception as e:
                        self.show_error_dialog(f"Error{e}")
                else:
                    query_data = {
                        "USERNAME": self.username,
                        "QUERY": str(support_field)
                    }
                    try:
                        reponse1 = requests.patch(f"{url}/{1}.json", json=query_data)
                        if reponse1.status_code == 200:
                            self.add_message(
                                "The Problem and been reached to library admin, Please wait the problem will be solved as soon as possible.",
                                from_user=False)
                    except Exception as e:
                        self.show_error_dialog(f"Error{e}")

            except Exception as e:
                self.show_error_dialog(f"Error {e}")
        else:
            self.show_error_dialog("Please type your problem")

    def logout(self):
        self.root.current = "home"

    def book_seat(self):
        date_select = MDDatePicker(min_date= dt.date.today())
        date_select.bind(on_save=self.on_date_selected, on_cancel=self.on_cancel)
        date_select.open()
        self.time_picker = TimePickerDialog()
        # self.root.current = "hall_selection"

    def update_scroll_status(self, scroll_y):
        self.should_auto_scroll = scroll_y <= 0.1

    def seatselection(self, other):
        if (other == "UG Hall"):
            self.switch_to_seat_selection1()
        elif (other == "PG Hall"):
            self.switch_to_seat_selection2()
        else:
            self.show_error_dialog("Please Select the hall number")

    def on_date_selected(self, instance, value, date_range):
        if str(value) < dt.datetime.today().strftime("%Y-%m-%d"):
            self.show_error_dialog("Please select the date and time of today or in future")
        else:
            if value.weekday() == 6:  # 6 corresponds to Sunday
                self.show_error_dialog("Sunday is not selectable. Please choose another day.")
                self.root.current = "user_dashboard"
            else:
                self.date_value = value
                self.time_picker.from_on_time_selected = self.from_on_time_selected
                self.time_picker.to_on_time_selected = self.to_on_time_selected
                self.time_picker.switch_to_user_dashboard = self.switch_to_user_dashboard
                self.time_picker.switch_to_hall_selection = self.switch_to_hall_selection
                self.time_picker.open()
                self.formated_date = value.strftime('%d-%m-%Y')

    def on_cancel(self, instance, value):
        self.show_error_dialog("Please Select The Date")
        self.root.current = "user_dashboard"

    def show_error_dialog(self, message):
        if not self.dialog:
            self.dialog = MDDialog(
                text=message,
                buttons=[
                    MDRaisedButton(
                        text="OK",
                        on_release=lambda _: self.dialog.dismiss()
                    )
                ]
            )
        self.dialog.text = message
        self.dialog.open()

    def from_on_time_selected(self, selected_time1):
        self.from_selected_time = dt.datetime.strptime(selected_time1, "%H:%M").time()

    def to_on_time_selected(self, selected_time2):
        self.to_selected_time = dt.datetime.strptime(selected_time2, "%H:%M").time()

    def on_enter_on_hall(self):
        if self.date_value and self.to_selected_time is not None:
            end_datetime = dt.datetime.combine(self.date_value, self.to_selected_time)
            now_time = dt.datetime.now()
            if now_time> end_datetime:
                self.show_error_dialog("The selected time range has already passed for today.")
                self.switch_to_user_dashboard()
            else:
                self.switch_to_hall_selection()

    def on_pre_enter_on_seat_selection1(self):
        path = "Upcoming_Booking"
        url = f"{self.firebase_url}/{path}.json"
        formatted_date = self.date_value.strftime("%d-%m-%Y")
        current_time = dt.datetime.now()
        try:
            response = requests.get(url)
            if response.status_code == 200:
                upcomming_data = response.json()
                if isinstance(upcomming_data,list):
                    for upcoming_details in upcomming_data:
                        if isinstance(upcoming_details,dict):
                            booked_by = upcoming_details.get("booked_by")
                            up_date = upcoming_details.get("date")
                            from_time = upcoming_details.get("from_time")
                            to_time = upcoming_details.get("to_time")
                            seat_no = upcoming_details.get("seat_no")
                            if (str(up_date)== str(formatted_date) and str(from_time)==str(self.from_selected_time) and str(self.to_selected_time)==str(to_time) and booked_by != None):
                                print("True")
                                self.disabled_seat1(seat_no)
                            else:
                                print("False")
                                self.enable_seat1(seat_no)

        except Exception as e:
            error_details = traceback.format_exc()
            self.show_error_dialog(f"Error: {e}\nDetails:\n{error_details}")

    def on_pre_enter_on_seat_selection2(self):
        path = "Upcoming_Booking"
        url = f"{self.firebase_url}/{path}.json"
        formatted_date = self.date_value.strftime("%d-%m-%Y")
        current_time = dt.datetime.now()
        formatted_time = current_time.strftime("%d-%m-%Y %H:%M:%S")
        try:
            response = requests.get(url)
            if response.status_code == 200:
                upcomming_data = response.json()

                if isinstance(upcomming_data,list):
                    for upcoming_details in upcomming_data:
                        if isinstance(upcoming_details,dict):
                            booked_by = upcoming_details.get("booked_by")
                            up_date = upcoming_details.get("date")
                            from_time = upcoming_details.get("from_time")
                            to_time = upcoming_details.get("to_time")
                            seat_no = upcoming_details.get("seat_no")
                            if (str(up_date)== str(formatted_date) and str(from_time)==str(self.from_selected_time) and str(self.to_selected_time)==str(to_time) and booked_by != None):
                                print("True")
                                self.disabled_seat2(seat_no)
                            else:
                                print("False")
                                self.enable_seat2(seat_no)


        except Exception as e:
            error_details = traceback.format_exc()
            self.show_error_dialog(f"Error: {e}\nDetails:\n{error_details}")

    def check_seat_availability1(self, other):
        if self.bldr.get_screen("seat_selection1").ids.seat1.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat1.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat2.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat2.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat3.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat3.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat4.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat4.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat5.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat5.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat6.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat6.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat7.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat7.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat8.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat8.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat9.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat9.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat10.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat10.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat11.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat11.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat12.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat12.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat13.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat13.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat14.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat14.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat15.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat15.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat16.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat16.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat17.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat17.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat18.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat18.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat19.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat19.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat20.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat20.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat21.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat21.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat22.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat22.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat23.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat23.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat24.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat24.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat25.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat25.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat26.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat26.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat27.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat27.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat28.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat28.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat29.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat29.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat30.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat30.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat31.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat31.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat32.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat32.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat33.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat33.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat34.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat34.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat35.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat35.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat36.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat36.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat37.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat37.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat38.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat38.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat39.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat39.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat40.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat40.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat41.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat41.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat42.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat42.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat43.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat43.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat44.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat44.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat45.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat45.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat46.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat46.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat47.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat47.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat48.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat48.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat49.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat49.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat50.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat50.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat51.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat51.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat52.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat52.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat53.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat53.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat54.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat54.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat55.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat55.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat56.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat56.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat57.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat57.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat58.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat58.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat59.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat59.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat60.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat60.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat61.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat61.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat62.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat62.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat63.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat63.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat64.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat64.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat65.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat65.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat66.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat66.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat67.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat67.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat68.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat68.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat69.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat69.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat70.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat70.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat71.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat71.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat72.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat72.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat73.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat73.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat74.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat74.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat75.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat75.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat76.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat76.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat77.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat77.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat78.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat78.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat79.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat79.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat80.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat80.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat81.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat81.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat82.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat82.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat83.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat83.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat84.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat84.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking1(other)
        else:
            self.show_error_dialog("Please Select the Seat To Book!")

    def check_seat_availability2(self,other):
        if self.bldr.get_screen("seat_selection2").ids.seat1.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat1.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat2.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat2.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat3.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat3.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat4.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat4.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat5.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat5.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat6.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat6.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat7.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat7.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat8.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat8.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat9.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat9.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat10.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat10.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat11.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat11.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat12.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat12.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat13.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat13.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat14.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat14.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat15.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat15.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat16.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat16.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat17.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat17.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat18.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat18.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat19.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat19.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat20.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat20.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat21.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat21.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat22.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat22.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat23.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat23.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat24.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat24.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat25.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat25.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat26.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat26.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat27.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat27.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat28.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat28.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat29.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat29.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat30.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat30.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat31.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat31.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat32.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat32.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat33.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat33.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat34.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat34.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat35.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat35.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat36.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat36.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat37.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat37.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat38.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat38.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat39.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat39.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat40.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat40.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat41.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat41.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat42.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat42.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat43.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat43.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat44.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat44.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat45.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat45.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat46.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat46.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat47.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat47.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat48.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat48.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat49.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat49.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat50.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat50.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat51.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat51.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat52.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat52.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat53.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat53.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat54.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat54.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat55.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat55.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat56.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat56.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat57.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat57.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat58.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat58.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat59.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat59.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat60.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat60.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat61.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat61.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat62.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat62.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat63.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat63.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat64.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat64.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat65.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat65.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat66.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat66.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat67.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat67.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat68.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat68.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat69.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat69.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat70.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat70.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat71.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat71.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat72.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat72.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat73.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat73.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat74.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat74.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat75.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat75.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat76.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat76.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat77.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat77.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat78.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat78.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat79.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat79.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat80.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat80.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat81.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat81.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat82.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat82.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat83.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat83.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat84.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat84.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.seat_booking2(other)
        else:
            self.show_error_dialog("Please Select the Seat To Book!")
    def seat_booking1(self,other):
        seat_id1 = other
        now_time = dt.datetime.now()
        today_datetime = dt.datetime.combine(dt.date.today(), dt.time())
        start_datetime = dt.datetime.combine(self.date_value, self.from_selected_time)
        end_datetime = dt.datetime.combine(self.date_value, self.to_selected_time)
        if self.date_value >= dt.date.today():
            if self.date_value == dt.date.today():
                if start_datetime <= now_time <= end_datetime:
                    path = "hall_A_seat_details"
                    url = f"{self.firebase_url}/{path}.json"

                    try:
                        response = requests.get(url)
                        if response.status_code == 200:
                            seat_data = response.json()
                            validated_seat = None
                            seat_id = None
                            if isinstance(seat_data,list):
                                for seat_id_key, seat_details in enumerate(seat_data):
                                    if isinstance(seat_details, dict):
                                        seat_name = seat_details.get("seat_name")
                                        seat_status = seat_details.get("status")
                                        seat_avail = seat_details.get("Booked_by")
                                        if seat_id1 is not None:
                                            if seat_name == seat_id1 and seat_status == "available" and seat_avail == "None":
                                                validated_seat = {
                                                    "seat_id": seat_name,
                                                    "status": "available",
                                                    "Booked_by": "None"
                                                }
                                                seat_id = seat_id_key
                                                break
                                if validated_seat and seat_id:
                                    update_url = f"{self.firebase_url}/{path}/{seat_id}.json"
                                    update_data = json.dumps({"status": "Booked", "Booked_by": self.username})
                                    update_response = requests.patch(update_url, data=update_data)
                                    if update_response.status_code == 200:
                                        self.show_error_dialog("Successfully, Seat Booked")
                                        self.switch_to_user_dashboard()
                                    else:
                                        self.show_error_dialog(
                                            f"Failed to Book Seat: {response.status_code}, {response.text}")
                    except Exception as e:
                        self.show_error_dialog(f"Error,{e}")
                    time.sleep(1)
                    seat_name = None
                    try:
                        response = requests.get(url)
                        if response.status_code == 200:
                            seat_data = response.json()
                            validated_seat = None
                            seat_id3 = None
                            if isinstance(seat_data, list):
                                for seat_details in seat_data:
                                    if isinstance(seat_details, dict):
                                        seat_ids = seat_details.get("seat_name")
                                        seat_status = seat_details.get("status")
                                        seat_avail = seat_details.get("Booked_by")

                                        if seat_id1 is not None:
                                            if seat_ids == seat_id1 and seat_status == "Booked" and seat_avail == self.username:
                                                validated_seat = {
                                                    "seat_id": seat_ids,
                                                    "status": "Booked",
                                                    "Booked_by": self.username
                                                }
                                                seat_id3 = seat_ids
                                                break

                                if validated_seat and seat_id3:
                                    seat_name = seat_id3
                    except Exception as e:
                        self.show_error_dialog(f"Error,{e}")
                    if today_datetime < start_datetime:
                        path1 = "Upcoming_Booking"
                        url1 = f"{self.firebase_url}/{path1}.json"
                        if seat_name is not None:
                            upcoming_booking_data = dict(seat_no=seat_name, date=str(self.formated_date),
                                                         from_time=str(self.from_selected_time),
                                                         to_time=str(self.to_selected_time), booked_by=str(self.username))

                            try:
                                response3 = requests.get(url1)
                                if response3.status_code == 200:
                                    existing_data = response3.json()
                                    upcoming_id = []
                                    if existing_data is not None:
                                        for id1, details in enumerate(existing_data):
                                            upcoming_id.append(id1)
                                        next_id = max(upcoming_id)+1
                                    else:
                                        next_id = 1
                                    try:
                                        response1 = requests.put(f"{self.firebase_url}/{path1}/{next_id}.json", json=upcoming_booking_data)
                                        if response1.status_code == 200:
                                            self.show_error_dialog("Successfully, Seat Booked")
                                        else:
                                            self.show_error_dialog("Unable to book seat!")
                                    except Exception as e:
                                        self.show_error_dialog(f"Error {e}")
                            except Exception as e:
                                self.show_error_dialog(f"Error {e}")
                        else:
                            self.show_error_dialog("Please Select the Seat")
                    else:
                        path2 = "Past_booking"
                        url2 = f"{self.firebase_url}/{path2}.json"
                        past_booking_data = {
                            "seat_no": seat_name,
                            "date": str(self.formated_date),
                            "from_time": str(self.from_selected_time),
                            "to_time": str(self.to_selected_time),
                            "booked_by": str(self.username)
                        }
                        try:
                            response1 = requests.get(url2)
                            if response1.status_code == 200:
                                existing_data = response1.json()
                                if existing_data is not None:
                                    past_id = []
                                    for id1 , details in enumerate(existing_data):
                                        past_id.append(id1)
                                    next_id = max(past_id)+1
                                else:
                                    next_id=1
                                try:
                                    past_response = requests.put(f"{self.firebase_url}/{path2}/{next_id}.json",json=past_booking_data)
                                    if past_response.status_code == 200 :
                                        self.show_error_dialog("Seat Booked")
                                except Exception as e:
                                    self.show_error_dialog(f"Error {e}")
                        except Exception as e:
                            self.show_error_dialog(f"Error {e}")
                    self.disabled_seat1(seat_name)
                elif now_time < start_datetime:
                    if today_datetime < start_datetime:
                        path1 = "Upcoming_Booking"
                        url1 = f"{self.firebase_url}/{path1}.json"
                        if seat_id1 is not None:
                            upcoming_booking_data = {
                                "seat_no": seat_id1,
                                "date": str(self.formated_date),
                                "from_time": str(self.from_selected_time),
                                "to_time": str(self.to_selected_time),
                                "booked_by": str(self.username)
                            }

                            try:
                                response3 = requests.get(url1)
                                if response3.status_code == 200:
                                    existing_data = response3.json()
                                    upcoming_id = []
                                    if existing_data is not None:
                                        for id1, details in enumerate(existing_data):
                                            upcoming_id.append(id1)
                                        next_id = max(upcoming_id) + 1
                                    else:
                                        next_id = 1
                                    try:
                                        response1 = requests.put(f"{self.firebase_url}/{path1}/{next_id}.json",
                                                                 json=upcoming_booking_data)
                                        if response1.status_code == 200:
                                            self.show_error_dialog("Successfully, Seat Booked")
                                        else:
                                            self.show_error_dialog("Unable to book seat!")
                                    except Exception as e:
                                        self.show_error_dialog(f"Error {e}")
                            except Exception as e:
                                self.show_error_dialog(f"Error {e}")

                    else:
                        path2 = "Past_booking"
                        url2 = f"{self.firebase_url}/{path2}.json"
                        if seat_id1 is not None:
                            past_booking_data = {
                                "seat_no": seat_id1,
                                "date": str(self.formated_date),
                                "from_time": str(self.from_selected_time),
                                "to_time": str(self.to_selected_time),
                                "booked_by": str(self.username)
                            }
                            try:
                                response1 = requests.get(url2)
                                if response1.status_code == 200:
                                    existing_data = response1.json()
                                    if existing_data is not None:
                                        past_id = []
                                        for id1, details in enumerate(existing_data):
                                            past_id.append(id1)
                                        next_id = max(past_id) + 1
                                    else:
                                        next_id = 1
                                    try:
                                        past_response = requests.put(f"{self.firebase_url}/{path2}/{next_id}.json",
                                                                     json=past_booking_data)
                                        if past_response.status_code == 200:
                                            self.show_error_dialog("Seat Booked")
                                    except Exception as e:
                                        self.show_error_dialog(f"Error {e}")
                            except Exception as e:
                                self.show_error_dialog(f"Error {e}")
                    # Clock.schedule_once(self.enable_seat, end_delay)
                else:
                    self.show_error_dialog("The selected time range has already passed for today.")
            elif self.date_value > dt.date.today():
                if (today_datetime < start_datetime):
                    path1 = "Upcoming_Booking"
                    url1 = f"{self.firebase_url}/{path1}.json"
                    if seat_id1 is not None:
                        upcoming_booking_data = {
                            "seat_no": seat_id1,
                            "date": str(self.formated_date),
                            "from_time": str(self.from_selected_time),
                            "to_time": str(self.to_selected_time),
                            "booked_by": str(self.username)
                        }

                        try:
                            response3 = requests.get(url1)
                            if response3.status_code == 200:
                                existing_data = response3.json()
                                upcoming_id = []
                                if existing_data is not None:
                                    for id1, details in enumerate(existing_data):
                                        upcoming_id.append(id1)
                                    next_id = max(upcoming_id) + 1
                                else:
                                    next_id = 1
                                try:
                                    response1 = requests.put(f"{self.firebase_url}/{path1}/{next_id}.json",
                                                             json=upcoming_booking_data)
                                    if response1.status_code == 200:
                                        self.show_error_dialog("Successfully, Seat Booked")
                                    else:
                                        self.show_error_dialog("Unable to book seat!")
                                except Exception as e:
                                    self.show_error_dialog(f"Error {e}")
                        except Exception as e:
                            self.show_error_dialog(f"Error {e}")

                else:
                    path2 = "Past_booking"
                    url2 = f"{self.firebase_url}/{path2}.json"
                    if seat_id1 is not None:
                        past_booking_data = {
                            "seat_no": seat_id1,
                            "date": str(self.formated_date),
                            "from_time": str(self.from_selected_time),
                            "to_time": str(self.to_selected_time),
                            "booked_by": str(self.username)
                        }
                        try:
                            response1 = requests.get(url2)
                            if response1.status_code == 200:
                                existing_data = response1.json()
                                if existing_data is not None:
                                    past_id = []
                                    for id1, details in enumerate(existing_data):
                                        past_id.append(id1)
                                    next_id = max(past_id) + 1
                                else:
                                    next_id = 1
                                try:
                                    past_response = requests.put(f"{self.firebase_url}/{path2}/{next_id}.json",
                                                                 json=past_booking_data)
                                    if past_response.status_code == 200:
                                        self.show_error_dialog("Seat Booked")
                                except Exception as e:
                                    self.show_error_dialog(f"Error {e}")
                        except Exception as e:
                            self.show_error_dialog(f"Error {e}")
                # Clock.schedule_once(self.enable_seat, end_delay)
        else:
            self.show_error_dialog("Please select a valid date in the future or today.")
    def seat_booking2(self,other):
        seat_id2 = other
        now_time = dt.datetime.now()
        today_datetime = dt.datetime.combine(dt.date.today(), dt.time())
        start_datetime = dt.datetime.combine(self.date_value, self.from_selected_time)
        end_datetime = dt.datetime.combine(self.date_value, self.to_selected_time)
        if self.date_value >= dt.date.today():
            if self.date_value == dt.date.today():
                if start_datetime <= now_time <= end_datetime:
                    path = "hall_B_seat_details"
                    url = f"{self.firebase_url}/{path}.json"

                    try:
                        response = requests.get(url)
                        if response.status_code == 200:
                            seat_data = response.json()
                            validated_seat = None
                            seat_id = None
                            for seat_id_key, seat_details in enumerate(seat_data):
                                if isinstance(seat_details, dict):
                                    seat_name = seat_details.get("seat_name")
                                    seat_status = seat_details.get("status")
                                    seat_avail = seat_details.get("Booked_by")
                                    if seat_id2 is not None:
                                        if seat_name == seat_id2 and seat_status == "available" and seat_avail == "None":
                                            validated_seat = {
                                                "seat_id": seat_name,
                                                "status": "available",
                                                "Booked_by": "None"
                                            }
                                            seat_id = seat_id_key
                                            break
                            if validated_seat and seat_id2:
                                update_url = f"{self.firebase_url}/{path}/{seat_id}.json"
                                update_data = json.dumps({"status": "Booked", "Booked_by": self.username})
                                update_response = requests.patch(update_url, data=update_data)
                                if update_response.status_code == 200:
                                    self.show_error_dialog("Successfully, Seat Booked")

                                else:
                                    self.show_error_dialog(
                                        f"Failed to Book Seat: {response.status_code}, {response.text}")
                    except Exception as e:
                        self.show_error_dialog(f"Error,{e}")
                    time.sleep(1)
                    seat_name = None
                    try:
                        response = requests.get(url)
                        if response.status_code == 200:
                            seat_data = response.json()
                            validated_seat = None

                            seat_id3 = None
                            if isinstance(seat_data, list):
                                for seat_details in seat_data:
                                    if isinstance(seat_details, dict):
                                        seat_ids = seat_details.get("seat_name")
                                        seat_status = seat_details.get("status")
                                        seat_avail = seat_details.get("Booked_by")

                                        if seat_id2 is not None:
                                            if seat_ids == seat_id2 and seat_status == "Booked" and seat_avail == self.username:
                                                validated_seat = {
                                                    "seat_id": seat_ids,
                                                    "status": "Booked",
                                                    "Booked_by": self.username
                                                }
                                                seat_id3 = seat_ids
                                                break

                                if validated_seat and seat_id3:
                                    seat_name = seat_id3
                    except Exception as e:
                        self.show_error_dialog(f"Error,{e}")
                    if today_datetime < start_datetime:
                        path1 = "Upcoming_Booking"
                        url1 = f"{self.firebase_url}/{path1}.json"
                        if seat_name is not None:
                            upcoming_booking_data = dict(seat_no=seat_name, date=str(self.formated_date),
                                                         from_time=str(self.from_selected_time),
                                                         to_time=str(self.to_selected_time), booked_by=str(self.username))

                            try:
                                response3 = requests.get(url1)
                                if response3.status_code == 200:
                                    existing_data = response3.json()
                                    upcoming_id = []
                                    if existing_data is not None:
                                        for id1, details in enumerate(existing_data):
                                            upcoming_id.append(id1)

                                            next_id = max(upcoming_id)+1
                                    else:
                                        next_id = 1
                                    print(upcoming_id)
                                    try:
                                        response1 = requests.put(f"{self.firebase_url}/{path1}/{next_id}.json", json=upcoming_booking_data)
                                        if response1.status_code == 200:
                                            self.show_error_dialog("Successfully, Seat Booked")
                                        else:
                                            self.show_error_dialog("Unable to book seat!")
                                    except Exception as e:
                                        self.show_error_dialog(f"Error {e}")
                            except Exception as e:
                                self.show_error_dialog(f"Error {e}")
                        else:
                            self.show_error_dialog("Please Select The Seat")
                    else:
                        path2 = "Past_booking"
                        url2 = f"{self.firebase_url}/{path2}.json"
                        if seat_name is not None:
                            past_booking_data = {
                                "seat_no": seat_name,
                                "date": str(self.formated_date),
                                "from_time": str(self.from_selected_time),
                                "to_time": str(self.to_selected_time),
                                "booked_by": str(self.username)
                            }
                            try:
                                response1 = requests.get(url2)
                                if response1.status_code == 200:
                                    existing_data = response1.json()
                                    if existing_data is not None:
                                        past_id = []
                                        for id1 , details in enumerate(existing_data):
                                            past_id.append(id1)
                                        next_id = max(past_id)+1
                                    else:
                                        next_id=1
                                    try:
                                        past_response = requests.put(f"{self.firebase_url}/{path2}/{next_id}.json",json=past_booking_data)
                                        if past_response.status_code == 200 :
                                            self.show_error_dialog("Seat Booked")
                                    except Exception as e:
                                        self.show_error_dialog(f"Error {e}")
                            except Exception as e:
                                self.show_error_dialog(f"Error {e}")
                        else:
                            self.show_error_dialog("Please Select the seat")
                    self.disabled_seat1(seat_name)
                elif (now_time < start_datetime):
                    if (today_datetime < start_datetime):
                        path1 = "Upcoming_Booking"
                        url1 = f"{self.firebase_url}/{path1}.json"
                        if seat_id2 is not None:
                            upcoming_booking_data = {
                                "seat_no": seat_id2,
                                "date": str(self.formated_date),
                                "from_time": str(self.from_selected_time),
                                "to_time": str(self.to_selected_time),
                                "booked_by": str(self.username)
                            }

                            try:
                                response3 = requests.get(url1)
                                if response3.status_code == 200:
                                    existing_data = response3.json()
                                    upcoming_id = []
                                    if existing_data is not None:
                                        for id1, details in enumerate(existing_data):
                                            upcoming_id.append(id1)
                                        next_id = max(upcoming_id) + 1
                                    else:
                                        next_id = 1
                                    try:
                                        response1 = requests.put(f"{self.firebase_url}/{path1}/{next_id}.json",
                                                                 json=upcoming_booking_data)
                                        if response1.status_code == 200:
                                            self.show_error_dialog("Successfully, Seat Booked")
                                        else:
                                            self.show_error_dialog("Unable to book seat!")
                                    except Exception as e:
                                        self.show_error_dialog(f"Error {e}")
                            except Exception as e:
                                self.show_error_dialog(f"Error {e}")

                    else:
                        path2 = "Past_booking"
                        url2 = f"{self.firebase_url}/{path2}.json"
                        if seat_id2 is not None:
                            past_booking_data = {
                                "seat_no": seat_id2,
                                "date": str(self.formated_date),
                                "from_time": str(self.from_selected_time),
                                "to_time": str(self.to_selected_time),
                                "booked_by": str(self.username)
                            }
                            try:
                                response1 = requests.get(url2)
                                if response1.status_code == 200:
                                    existing_data = response1.json()
                                    if existing_data is not None:
                                        past_id = []
                                        for id1, details in enumerate(existing_data):
                                            past_id.append(id1)
                                        next_id = max(past_id) + 1
                                    else:
                                        next_id = 1
                                    try:
                                        past_response = requests.put(f"{self.firebase_url}/{path2}/{next_id}.json",
                                                                     json=past_booking_data)
                                        if past_response.status_code == 200:
                                            self.show_error_dialog("Seat Booked")
                                    except Exception as e:
                                        self.show_error_dialog(f"Error {e}")
                            except Exception as e:
                                self.show_error_dialog(f"Error {e}")
                    # Clock.schedule_once(self.enable_seat, end_delay)
                else:
                    self.show_error_dialog("The selected time range has already passed for today.")
            elif self.date_value > dt.date.today():
                if today_datetime < start_datetime:
                    path1 = "Upcoming_Booking"
                    url1 = f"{self.firebase_url}/{path1}.json"
                    if seat_id2 is not None:
                        upcoming_booking_data = {
                            "seat_no": seat_id2,
                            "date": str(self.formated_date),
                            "from_time": str(self.from_selected_time),
                            "to_time": str(self.to_selected_time),
                            "booked_by": str(self.username)
                        }

                        try:
                            response3 = requests.get(url1)
                            if response3.status_code == 200:
                                existing_data = response3.json()
                                upcoming_id = []
                                if existing_data is not None:
                                    for id1, details in enumerate(existing_data):
                                        upcoming_id.append(id1)
                                    next_id = max(upcoming_id) + 1
                                else:
                                    next_id = 1
                                try:
                                    response1 = requests.put(f"{self.firebase_url}/{path1}/{next_id}.json",
                                                             json=upcoming_booking_data)
                                    if response1.status_code == 200:
                                        self.show_error_dialog("Successfully, Seat Booked")
                                    else:
                                        self.show_error_dialog("Unable to book seat!")
                                except Exception as e:
                                    self.show_error_dialog(f"Error {e}")
                        except Exception as e:
                            self.show_error_dialog(f"Error {e}")

                else:
                    path2 = "Past_booking"
                    url2 = f"{self.firebase_url}/{path2}.json"
                    if seat_id2 is not None:
                        past_booking_data = {
                            "seat_no": seat_id2,
                            "date": str(self.formated_date),
                            "from_time": str(self.from_selected_time),
                            "to_time": str(self.to_selected_time),
                            "booked_by": str(self.username)
                        }
                        try:
                            response1 = requests.get(url2)
                            if response1.status_code == 200:
                                existing_data = response1.json()
                                if existing_data is not None:
                                    past_id = []
                                    for id1, details in enumerate(existing_data):
                                        past_id.append(id1)
                                    next_id = max(past_id) + 1
                                else:
                                    next_id = 1
                                try:
                                    past_response = requests.put(f"{self.firebase_url}/{path2}/{next_id}.json",
                                                                 json=past_booking_data)
                                    if past_response.status_code == 200:
                                        self.show_error_dialog("Seat Booked")
                                except Exception as e:
                                    self.show_error_dialog(f"Error {e}")
                        except Exception as e:
                            self.show_error_dialog(f"Error {e}")
                # Clock.schedule_once(self.enable_seat, end_delay)
        else:
            self.show_error_dialog("Please select a valid date in the future or today.")

    def disabled_seat1(self,seat_name):
        if self.bldr.get_screen("seat_selection1").ids.seat1.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat1.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat2.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat2.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat3.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat3.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat4.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat4.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat5.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat5.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat6.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat6.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat7.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat7.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat8.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat8.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat9.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat9.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat10.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat10.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat11.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat11.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat12.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat12.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat13.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat13.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat14.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat14.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat15.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat15.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat16.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat16.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat17.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat17.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat18.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat18.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat19.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat19.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat20.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat20.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat21.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat21.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat22.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat22.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat23.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat23.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat24.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat24.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat25.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat25.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat26.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat26.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat27.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat27.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat28.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat28.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat29.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat29.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat30.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat30.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat31.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat31.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat32.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat32.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat33.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat33.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat34.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat34.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat35.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat35.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat36.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat36.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat37.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat37.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat38.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat38.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat39.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat39.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat40.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat40.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat41.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat41.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat42.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat42.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat43.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat43.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat44.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat44.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat45.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat45.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat46.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat46.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat47.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat47.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat48.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat48.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat49.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat49.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat50.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat50.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat51.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat51.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat52.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat52.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat53.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat53.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat54.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat54.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat55.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat55.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat56.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat56.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat57.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat57.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat58.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat58.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat59.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat59.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat60.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat60.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat61.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat61.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat62.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat62.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat63.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat63.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat64.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat64.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat65.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat65.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat66.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat66.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat67.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat67.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat68.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat68.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat69.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat69.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat70.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat70.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat71.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat71.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat72.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat72.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat73.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat73.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat74.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat74.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat75.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat75.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat76.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat76.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat77.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat77.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat78.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat78.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat79.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat79.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat80.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat80.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat81.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat81.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat82.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat82.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat83.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat83.disabled = True
        elif self.bldr.get_screen("seat_selection1").ids.seat84.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat84.disabled = True
        else:
            self.show_error_dialog("Please Select Seat")

    def disabled_seat2(self, seat_name):
        if self.bldr.get_screen("seat_selection2").ids.seat1.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat1.disabled = True
        elif self.bldr.get_screen("seat_selection2").ids.seat2.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat2.disabled = True
        elif self.bldr.get_screen("seat_selection2").ids.seat3.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat3.disabled = True
        elif self.bldr.get_screen("seat_selection2").ids.seat4.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat4.disabled = True
        elif self.bldr.get_screen("seat_selection2").ids.seat5.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat5.disabled = True
        elif self.bldr.get_screen("seat_selection2").ids.seat6.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat6.disabled = True
        elif self.bldr.get_screen("seat_selection2").ids.seat7.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat7.disabled = True
        elif self.bldr.get_screen("seat_selection2").ids.seat8.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat8.disabled = True
        elif self.bldr.get_screen("seat_selection2").ids.seat9.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat9.disabled = True
        elif self.bldr.get_screen("seat_selection2").ids.seat10.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat10.disabled = True
        elif self.bldr.get_screen("seat_selection2").ids.seat11.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat11.disabled = True
        elif self.bldr.get_screen("seat_selection2").ids.seat12.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat12.disabled = True
        elif self.bldr.get_screen("seat_selection2").ids.seat13.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat13.disabled = True
        elif self.bldr.get_screen("seat_selection2").ids.seat14.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat14.disabled = True
        elif self.bldr.get_screen("seat_selection2").ids.seat15.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat15.disabled = True
        elif self.bldr.get_screen("seat_selection2").ids.seat16.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat16.disabled = True
        elif self.bldr.get_screen("seat_selection2").ids.seat17.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat17.disabled = True
        elif self.bldr.get_screen("seat_selection2").ids.seat18.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat18.disabled = True
        elif self.bldr.get_screen("seat_selection2").ids.seat19.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat19.disabled = True
        elif self.bldr.get_screen("seat_selection2").ids.seat20.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat20.disabled = True
        elif self.bldr.get_screen("seat_selection2").ids.seat21.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat21.disabled = True
        elif self.bldr.get_screen("seat_selection2").ids.seat22.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat22.disabled = True
        elif self.bldr.get_screen("seat_selection2").ids.seat23.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat23.disabled = True
        elif self.bldr.get_screen("seat_selection2").ids.seat24.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat24.disabled = True
        elif self.bldr.get_screen("seat_selection2").ids.seat25.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat25.disabled = True
        elif self.bldr.get_screen("seat_selection2").ids.seat26.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat26.disabled = True
        elif self.bldr.get_screen("seat_selection2").ids.seat27.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat27.disabled = True
        elif self.bldr.get_screen("seat_selection2").ids.seat28.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat28.disabled = True
        elif self.bldr.get_screen("seat_selection2").ids.seat29.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat29.disabled = True
        elif self.bldr.get_screen("seat_selection2").ids.seat30.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat30.disabled = True
        elif self.bldr.get_screen("seat_selection2").ids.seat31.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat31.disabled = True
        elif self.bldr.get_screen("seat_selection2").ids.seat32.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat32.disabled = True
        elif self.bldr.get_screen("seat_selection2").ids.seat33.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat33.disabled = True
        elif self.bldr.get_screen("seat_selection2").ids.seat34.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat34.disabled = True
        elif self.bldr.get_screen("seat_selection2").ids.seat35.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat35.disabled = True
        elif self.bldr.get_screen("seat_selection2").ids.seat36.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat36.disabled = True
        elif self.bldr.get_screen("seat_selection2").ids.seat37.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat37.disabled = True
        elif self.bldr.get_screen("seat_selection2").ids.seat38.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat38.disabled = True
        elif self.bldr.get_screen("seat_selection2").ids.seat39.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat39.disabled = True
        elif self.bldr.get_screen("seat_selection2").ids.seat40.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat40.disabled = True
        elif self.bldr.get_screen("seat_selection2").ids.seat41.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat41.disabled = True
        elif self.bldr.get_screen("seat_selection2").ids.seat42.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat42.disabled = True
        elif self.bldr.get_screen("seat_selection2").ids.seat43.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat43.disabled = True
        elif self.bldr.get_screen("seat_selection2").ids.seat44.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat44.disabled = True
        elif self.bldr.get_screen("seat_selection2").ids.seat45.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat45.disabled = True
        elif self.bldr.get_screen("seat_selection2").ids.seat46.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat46.disabled = True
        elif self.bldr.get_screen("seat_selection2").ids.seat47.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat47.disabled = True
        elif self.bldr.get_screen("seat_selection2").ids.seat48.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat48.disabled = True
        elif self.bldr.get_screen("seat_selection2").ids.seat49.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat49.disabled = True
        elif self.bldr.get_screen("seat_selection2").ids.seat50.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat50.disabled = True
        elif self.bldr.get_screen("seat_selection2").ids.seat51.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat51.disabled = True
        elif self.bldr.get_screen("seat_selection2").ids.seat52.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat52.disabled = True
        elif self.bldr.get_screen("seat_selection2").ids.seat53.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat53.disabled = True
        elif self.bldr.get_screen("seat_selection2").ids.seat54.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat54.disabled = True
        elif self.bldr.get_screen("seat_selection2").ids.seat55.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat55.disabled = True
        elif self.bldr.get_screen("seat_selection2").ids.seat56.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat56.disabled = True
        elif self.bldr.get_screen("seat_selection2").ids.seat57.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat57.disabled = True
        elif self.bldr.get_screen("seat_selection2").ids.seat58.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat58.disabled = True
        elif self.bldr.get_screen("seat_selection2").ids.seat59.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat59.disabled = True
        elif self.bldr.get_screen("seat_selection2").ids.seat60.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat60.disabled = True
        elif self.bldr.get_screen("seat_selection2").ids.seat61.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat61.disabled = True
        elif self.bldr.get_screen("seat_selection2").ids.seat62.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat62.disabled = True
        elif self.bldr.get_screen("seat_selection2").ids.seat63.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat63.disabled = True
        elif self.bldr.get_screen("seat_selection2").ids.seat64.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat64.disabled = True
        elif self.bldr.get_screen("seat_selection2").ids.seat65.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat65.disabled = True
        elif self.bldr.get_screen("seat_selection2").ids.seat66.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat66.disabled = True
        elif self.bldr.get_screen("seat_selection2").ids.seat67.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat67.disabled = True
        elif self.bldr.get_screen("seat_selection2").ids.seat68.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat68.disabled = True
        elif self.bldr.get_screen("seat_selection2").ids.seat69.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat69.disabled = True
        elif self.bldr.get_screen("seat_selection2").ids.seat70.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat70.disabled = True
        elif self.bldr.get_screen("seat_selection2").ids.seat71.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat71.disabled = True
        elif self.bldr.get_screen("seat_selection2").ids.seat72.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat72.disabled = True
        elif self.bldr.get_screen("seat_selection2").ids.seat73.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat73.disabled = True
        elif self.bldr.get_screen("seat_selection2").ids.seat74.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat74.disabled = True
        elif self.bldr.get_screen("seat_selection2").ids.seat75.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat75.disabled = True
        elif self.bldr.get_screen("seat_selection2").ids.seat76.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat76.disabled = True
        elif self.bldr.get_screen("seat_selection2").ids.seat77.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat77.disabled = True
        elif self.bldr.get_screen("seat_selection2").ids.seat78.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat78.disabled = True
        elif self.bldr.get_screen("seat_selection2").ids.seat79.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat79.disabled = True
        elif self.bldr.get_screen("seat_selection2").ids.seat80.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat80.disabled = True
        elif self.bldr.get_screen("seat_selection2").ids.seat81.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat81.disabled = True
        elif self.bldr.get_screen("seat_selection2").ids.seat82.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat82.disabled = True
        elif self.bldr.get_screen("seat_selection2").ids.seat83.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat83.disabled = True
        elif self.bldr.get_screen("seat_selection2").ids.seat84.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat84.disabled = True
        else:
            self.show_error_dialog("Please Select Seat")

    def enable_seat1(self,seat_name):
        if self.bldr.get_screen("seat_selection1").ids.seat1.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat1.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat2.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat2.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat3.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat3.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat4.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat4.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat5.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat5.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat6.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat6.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat7.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat7.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat8.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat8.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat9.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat9.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat10.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat10.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat11.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat11.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat12.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat12.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat13.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat13.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat14.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat14.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat15.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat15.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat16.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat16.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat17.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat17.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat18.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat18.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat19.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat19.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat20.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat20.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat21.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat21.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat22.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat22.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat23.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat23.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat24.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat24.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat25.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat25.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat26.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat26.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat27.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat27.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat28.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat28.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat29.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat29.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat30.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat30.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat31.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat31.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat32.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat32.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat33.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat33.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat34.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat34.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat35.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat35.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat36.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat36.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat37.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat37.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat38.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat38.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat39.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat39.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat40.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat40.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat41.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat41.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat42.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat42.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat43.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat43.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat44.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat44.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat45.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat45.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat46.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat46.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat47.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat47.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat48.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat48.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat49.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat49.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat50.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat50.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat51.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat51.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat52.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat52.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat53.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat53.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat54.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat54.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat55.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat55.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat56.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat56.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat57.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat57.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat58.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat58.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat59.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat59.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat60.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat60.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat61.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat61.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat62.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat62.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat63.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat63.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat64.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat64.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat65.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat65.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat66.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat66.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat67.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat67.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat68.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat68.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat69.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat69.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat70.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat70.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat71.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat71.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat72.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat72.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat73.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat73.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat74.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat74.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat75.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat75.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat76.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat76.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat77.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat77.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat78.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat78.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat79.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat79.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat80.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat80.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat81.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat81.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat82.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat82.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat83.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat83.disabled = False
        elif self.bldr.get_screen("seat_selection1").ids.seat84.name == seat_name:
            self.bldr.get_screen("seat_selection1").ids.seat84.disabled = False

    def enable_seat2(self,seat_name):
        if self.bldr.get_screen("seat_selection2").ids.seat1.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat1.disabled = False
        elif self.bldr.get_screen("seat_selection2").ids.seat2.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat2.disabled = False
        elif self.bldr.get_screen("seat_selection2").ids.seat3.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat3.disabled = False
        elif self.bldr.get_screen("seat_selection2").ids.seat4.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat4.disabled = False
        elif self.bldr.get_screen("seat_selection2").ids.seat5.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat5.disabled = False
        elif self.bldr.get_screen("seat_selection2").ids.seat6.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat6.disabled = False
        elif self.bldr.get_screen("seat_selection2").ids.seat7.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat7.disabled = False
        elif self.bldr.get_screen("seat_selection2").ids.seat8.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat8.disabled = False
        elif self.bldr.get_screen("seat_selection2").ids.seat9.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat9.disabled = False
        elif self.bldr.get_screen("seat_selection2").ids.seat10.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat10.disabled = False
        elif self.bldr.get_screen("seat_selection2").ids.seat11.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat11.disabled = False
        elif self.bldr.get_screen("seat_selection2").ids.seat12.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat12.disabled = False
        elif self.bldr.get_screen("seat_selection2").ids.seat13.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat13.disabled = False
        elif self.bldr.get_screen("seat_selection2").ids.seat14.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat14.disabled = False
        elif self.bldr.get_screen("seat_selection2").ids.seat15.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat15.disabled = False
        elif self.bldr.get_screen("seat_selection2").ids.seat16.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat16.disabled = False
        elif self.bldr.get_screen("seat_selection2").ids.seat17.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat17.disabled = False
        elif self.bldr.get_screen("seat_selection2").ids.seat18.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat18.disabled = False
        elif self.bldr.get_screen("seat_selection2").ids.seat19.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat19.disabled = False
        elif self.bldr.get_screen("seat_selection2").ids.seat20.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat20.disabled = False
        elif self.bldr.get_screen("seat_selection2").ids.seat21.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat21.disabled = False
        elif self.bldr.get_screen("seat_selection2").ids.seat22.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat22.disabled = False
        elif self.bldr.get_screen("seat_selection2").ids.seat23.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat23.disabled = False
        elif self.bldr.get_screen("seat_selection2").ids.seat24.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat24.disabled = False
        elif self.bldr.get_screen("seat_selection2").ids.seat25.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat25.disabled = False
        elif self.bldr.get_screen("seat_selection2").ids.seat26.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat26.disabled = False
        elif self.bldr.get_screen("seat_selection2").ids.seat27.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat27.disabled = False
        elif self.bldr.get_screen("seat_selection2").ids.seat28.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat28.disabled = False
        elif self.bldr.get_screen("seat_selection2").ids.seat29.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat29.disabled = False
        elif self.bldr.get_screen("seat_selection2").ids.seat30.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat30.disabled = False
        elif self.bldr.get_screen("seat_selection2").ids.seat31.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat31.disabled = False
        elif self.bldr.get_screen("seat_selection2").ids.seat32.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat32.disabled = False
        elif self.bldr.get_screen("seat_selection2").ids.seat33.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat33.disabled = False
        elif self.bldr.get_screen("seat_selection2").ids.seat34.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat34.disabled = False
        elif self.bldr.get_screen("seat_selection2").ids.seat35.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat35.disabled = False
        elif self.bldr.get_screen("seat_selection2").ids.seat36.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat36.disabled = False
        elif self.bldr.get_screen("seat_selection2").ids.seat37.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat37.disabled = False
        elif self.bldr.get_screen("seat_selection2").ids.seat38.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat38.disabled = False
        elif self.bldr.get_screen("seat_selection2").ids.seat39.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat39.disabled = False
        elif self.bldr.get_screen("seat_selection2").ids.seat40.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat40.disabled = False
        elif self.bldr.get_screen("seat_selection2").ids.seat41.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat41.disabled = False
        elif self.bldr.get_screen("seat_selection2").ids.seat42.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat42.disabled = False
        elif self.bldr.get_screen("seat_selection2").ids.seat43.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat43.disabled = False
        elif self.bldr.get_screen("seat_selection2").ids.seat44.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat44.disabled = False
        elif self.bldr.get_screen("seat_selection2").ids.seat45.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat45.disabled = False
        elif self.bldr.get_screen("seat_selection2").ids.seat46.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat46.disabled = False
        elif self.bldr.get_screen("seat_selection2").ids.seat47.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat47.disabled = False
        elif self.bldr.get_screen("seat_selection2").ids.seat48.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat48.disabled = False
        elif self.bldr.get_screen("seat_selection2").ids.seat49.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat49.disabled = False
        elif self.bldr.get_screen("seat_selection2").ids.seat50.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat50.disabled = False
        elif self.bldr.get_screen("seat_selection2").ids.seat51.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat51.disabled = False
        elif self.bldr.get_screen("seat_selection2").ids.seat52.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat52.disabled = False
        elif self.bldr.get_screen("seat_selection2").ids.seat53.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat53.disabled = False
        elif self.bldr.get_screen("seat_selection2").ids.seat54.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat54.disabled = False
        elif self.bldr.get_screen("seat_selection2").ids.seat55.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat55.disabled = False
        elif self.bldr.get_screen("seat_selection2").ids.seat56.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat56.disabled = False
        elif self.bldr.get_screen("seat_selection2").ids.seat57.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat57.disabled = False
        elif self.bldr.get_screen("seat_selection2").ids.seat58.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat58.disabled = False
        elif self.bldr.get_screen("seat_selection2").ids.seat59.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat59.disabled = False
        elif self.bldr.get_screen("seat_selection2").ids.seat60.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat60.disabled = False
        elif self.bldr.get_screen("seat_selection2").ids.seat61.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat61.disabled = False
        elif self.bldr.get_screen("seat_selection2").ids.seat62.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat62.disabled = False
        elif self.bldr.get_screen("seat_selection2").ids.seat63.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat63.disabled = False
        elif self.bldr.get_screen("seat_selection2").ids.seat64.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat64.disabled = False
        elif self.bldr.get_screen("seat_selection2").ids.seat65.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat65.disabled = False
        elif self.bldr.get_screen("seat_selection2").ids.seat66.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat66.disabled = False
        elif self.bldr.get_screen("seat_selection2").ids.seat67.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat67.disabled = False
        elif self.bldr.get_screen("seat_selection2").ids.seat68.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat68.disabled = False
        elif self.bldr.get_screen("seat_selection2").ids.seat69.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat69.disabled = False
        elif self.bldr.get_screen("seat_selection2").ids.seat70.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat70.disabled = False
        elif self.bldr.get_screen("seat_selection2").ids.seat71.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat71.disabled = False
        elif self.bldr.get_screen("seat_selection2").ids.seat72.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat72.disabled = False
        elif self.bldr.get_screen("seat_selection2").ids.seat73.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat73.disabled = False
        elif self.bldr.get_screen("seat_selection2").ids.seat74.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat74.disabled = False
        elif self.bldr.get_screen("seat_selection2").ids.seat75.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat75.disabled = False
        elif self.bldr.get_screen("seat_selection2").ids.seat76.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat76.disabled = False
        elif self.bldr.get_screen("seat_selection2").ids.seat77.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat77.disabled = False
        elif self.bldr.get_screen("seat_selection2").ids.seat78.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat78.disabled = False
        elif self.bldr.get_screen("seat_selection2").ids.seat79.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat79.disabled = False
        elif self.bldr.get_screen("seat_selection2").ids.seat80.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat80.disabled = False
        elif self.bldr.get_screen("seat_selection2").ids.seat81.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat81.disabled = False
        elif self.bldr.get_screen("seat_selection2").ids.seat82.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat82.disabled = False
        elif self.bldr.get_screen("seat_selection2").ids.seat83.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat83.disabled = False
        elif self.bldr.get_screen("seat_selection2").ids.seat84.name == seat_name:
            self.bldr.get_screen("seat_selection2").ids.seat84.disabled = False

    def on_click(self,seat_no,seat_booked_by,list_item):
        self.dialog1 = MDDialog(
            title="Cancel Booking",
            text="Are you sure you want to cancel your booking?",
            buttons=[
                MDRaisedButton(
                    text="Yes",
                    on_release=lambda x:self.confirm_cancel(seat_booked_by,seat_no,list_item)
                ),
                MDRaisedButton(
                    text="No",
                    on_release=lambda _: self.dialog1.dismiss()
                ),
            ],
        )
        self.dialog1.open()

    def confirm_cancel(self,seat_booked_by,seat_no,list_item):
        path = "Upcoming_Booking"
        url = f"{self.firebase_url}/{path}"
        self.bldr.get_screen("upcoming_booking").ids.upcoming_booking.remove_widget(list_item)
        self.dialog1.dismiss()
        try:
            response = requests.get(f"{url}.json")
            if response.status_code==200:
                upcoming_data = response.json()
                if isinstance(upcoming_data,list):
                    for id1,booking_details in enumerate(upcoming_data):
                        if isinstance(booking_details,dict):
                            seat_no1 = booking_details.get("seat_no")
                            seat_booked_by1 = booking_details.get("booked_by")
                            if seat_no == seat_no1 and seat_booked_by == seat_booked_by1:
                                try:
                                    response1 = requests.delete(f"{url}/{id1}.json")
                                    if response1.status_code == 200:
                                        self.show_error_dialog("Booking has been canceled successfully!")
                                        self.executer.submit(self.enable_seat1(seat_no))
                                        self.executer.submit(self.enable_seat2(seat_no))
                                        self.upcoming_booking()
                                except Exception as e:
                                    self.show_error_dialog(f"Error {e}")
                                hall_A_path = "hall_A_seat_details"
                                hall_A_url = f"{self.firebase_url}/{hall_A_path}"
                                try:
                                    response = requests.get(f"{hall_A_url}.json")
                                    if response.status_code == 200:
                                        seat_data = response.json()
                                        if isinstance(seat_data, list):
                                            validated_seat = []
                                            # self.seat_id = None

                                            seat_id2 = None
                                            for seat_id_key, seat_details in enumerate(seat_data):
                                                if isinstance(seat_details, dict):
                                                    seat_ids = seat_details.get("seat_id")
                                                    seat_status = seat_details.get("status")
                                                    if seat_status == "Booked":
                                                        validated_seat.append(seat_id_key)
                                            if validated_seat:
                                                for i in validated_seat:
                                                    hall_A_data = json.dumps(
                                                        {"status": "available", "Booked_by": "None"})
                                                    update_response = requests.patch(f"{hall_A_url}/{i}.json",
                                                                                     data=hall_A_data)
                                                    if update_response.status_code == 200:
                                                        continue
                                except Exception as e:
                                    self.show_error_dialog(f"Error {e}")
                                hall_B_path = "hall_B_seat_details"
                                hall_B_url = f"{self.firebase_url}/{hall_B_path}"
                                try:
                                    response = requests.get(f"{hall_B_url}.json")
                                    if response.status_code == 200:
                                        seat_data = response.json()
                                        if isinstance(seat_data, list):
                                            validated_seat = []
                                            # self.seat_id = None

                                            seat_id2 = None
                                            for seat_id_key, seat_details in enumerate(seat_data):
                                                if isinstance(seat_details, dict):
                                                    seat_ids = seat_details.get("seat_id")
                                                    seat_status = seat_details.get("status")
                                                    if seat_status == "Booked":
                                                        validated_seat.append(seat_id_key)
                                            if validated_seat:
                                                for i in validated_seat:
                                                    hall_A_data = json.dumps(
                                                        {"status": "available", "Booked_by": "None"})
                                                    update_response = requests.patch(f"{hall_B_url}/{i}.json",
                                                                                     data=hall_A_data)
                                                    if update_response.status_code == 200:
                                                        continue
                                except Exception as e:
                                    self.show_error_dialog(f"Error {e}")
        except Exception as e :
            self.show_error_dialog(f"Error {e}")

    def upcoming_booking(self):
        self.bldr.get_screen("upcoming_booking").ids.upcoming_booking.clear_widgets()

        path1 = "Upcoming_Booking"
        url1 = f"{self.firebase_url}/{path1}"

        try:
            response = requests.get(f"{url1}.json")
            if response.status_code == 200:
                upcoming_data = response.json()
                if isinstance(upcoming_data, list):
                    for upcoming_details in upcoming_data:
                        if isinstance(upcoming_details, dict):
                            seat_no = upcoming_details.get("seat_no")
                            seat_date = upcoming_details.get("date")
                            seat_from_time = upcoming_details.get("from_time")
                            seat_to_time = upcoming_details.get("to_time")
                            seat_booked_by = upcoming_details.get("booked_by")
                            if seat_booked_by == self.username:
                                list_item = ThreeLineIconListItem(
                                    text=f"Seat No: {seat_no} ",
                                    secondary_text=f"Date: {seat_date}",
                                    tertiary_text=f"From Time: {seat_from_time} \n To Time: {seat_to_time}",
                                    on_release=lambda x, seat_no1=seat_no, seat_booked_by1=seat_booked_by: self.on_click(seat_no1, seat_booked_by1,list_item)
                                )
                                icon = IconLeftWidget(icon="calendar-check")
                                list_item.add_widget(icon)
                                self.bldr.get_screen("upcoming_booking").ids.upcoming_booking.add_widget(list_item)
        except Exception as e:
            self.show_error_dialog(f"Error {e}")
        self.root.current = "upcoming_booking"

    def past_booking(self):
        self.bldr.get_screen("past_booking").ids.past_booking.clear_widgets()
        path2 = "Past_booking"
        url2 = f"{self.firebase_url}/{path2}"
        try:
            response1 = requests.get(f"{url2}.json")
            if response1.status_code == 200:
                past_data = response1.json()
                if isinstance(past_data, list):
                    for past_details in past_data:
                        if isinstance(past_details, dict):
                            seat_no = past_details.get("seat_no")
                            seat_date = past_details.get("date")
                            seat_from_time = past_details.get("from_time")
                            seat_to_time = past_details.get("to_time")
                            seat_booked_by = past_details.get("booked_by")
                            if seat_booked_by == self.username:
                                list_item = ThreeLineIconListItem(
                                    text=f"Seat No: {seat_no} ",
                                    secondary_text=f"Date: {seat_date}",
                                    tertiary_text=f"From Time: {seat_from_time} \n To Time: {seat_to_time}"
                                )
                                icon = IconLeftWidget(icon="calendar-check")
                                list_item.add_widget(icon)
                                self.bldr.get_screen("past_booking").ids.past_booking.add_widget(list_item)
        except Exception as e:
            self.show_error_dialog(f"Error {e}")
        self.root.current = "past_booking"


if __name__ == '__main__':
    Window.size = (450, 600)
    SeatbookerApp().run()

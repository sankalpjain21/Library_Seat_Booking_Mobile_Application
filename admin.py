from kivy.uix.modalview import ModalView
from kivymd.app import MDApp
from kivymd.uix.button import MDFlatButton,MDRaisedButton
from kivy.lang.builder import Builder
import datetime as dt
import traceback
import time
from concurrent.futures import ThreadPoolExecutor
from kivymd.uix.dialog import MDDialog
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.list import ThreeLineIconListItem, IconLeftWidget, OneLineListItem
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.pickers import MDDatePicker
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.screen import MDScreen
from kivy.core.window import Window
import requests
import json
from kivy.uix.modalview import ModalView
from kivy.uix.spinner import Spinner
from calendar import monthrange
from kivy.uix.widget import Widget
from kivy.graphics import Rectangle
from kivy.graphics.context_instructions import Color
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField


class BarGraphWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.size_hint = (1, 0.7)
        self.opacity = 0  # Initially invisible
        self.labels = []  # Store labels for removal

    def set_data(self,year,month_name,weekly_counts):
        self.data = []
        weeks =[]
        self.selected_month = month_name
        if isinstance(weekly_counts,dict):
            for i ,j in weekly_counts.items():
                weeks.append(i)
                self.data.append(j)
        if "Week1" in weeks:pass
        else:self.data.append(0)
        if "Week2" in weeks:pass
        else:self.data.append(0)
        if "Week3" in weeks:pass
        else:self.data.append(0)
        if "Week4" in weeks:pass
        else:self.data.append(0)


    def clear_bars(self):
        """Clear previously drawn bars and labels."""
        self.canvas.clear()  # Clear the canvas (removes all drawings)
        for label in self.labels:
            label.text = ""  # Remove each label from the widget
        self.labels = []  # Reset the label list

    def draw_bars(self):
        """Draw bars for the given list of data."""
        self.clear_bars()  # Clear old bars and labels

        with self.canvas:
            bar_width = 80  # Width of each bar
            gap = 10  # Gap between bars
            max_height = max(self.data)  # Maximum value in the data for scaling
            if max_height is 0:
                scale_factor = 0
            else:
                scale_factor = self.height / (max_height * 2.5)  # Scale factor for bar heights

            start_x = 140
            start_y = 140


            # Loop through the data and draw bars
            for index, value in enumerate(self.data):
                x = start_x + index * (bar_width + gap)
                y = start_y
                height = value * scale_factor

                # Draw the bar with color
                Color(0.502, 0, 0.502, 1)  # Purple color
                Rectangle(pos=(x, y), size=(bar_width, height))

                # Add label for each bar
                label = MDLabel(
                    text=str(value),
                    color=(0, 0, 0, 1),
                    size_hint=(None, None),
                    size=(bar_width, 30),
                    pos=(x+35, y + height),
                )
                self.add_widget(label)
                self.labels.append(label)  # Store label for future removal
                week1_label = MDLabel(text="Week 1", color=(0, 0, 0, 1), size_hint=(None, None),
                                    size=(80, 30),
                                    pos=(start_x+5, 110))
                self.add_widget(week1_label)
                self.labels.append(week1_label)
                week2_label = MDLabel(text="Week 2", color=(0, 0, 0, 1), size_hint=(None, None),
                                    size=(80, 30),
                                    pos=(240, 110))
                self.add_widget(week2_label)
                self.labels.append(week2_label)
                week3_label = MDLabel(text="Week 3", color=(0, 0, 0, 1), size_hint=(None, None),
                                    size=(80, 30),
                                    pos=(335, 110))
                self.add_widget(week3_label)
                self.labels.append(week3_label)
                week4_label = MDLabel(text="Week 4", color=(0, 0, 0, 1), size_hint=(None, None),
                                    size=(80, 30),
                                    pos=(430, 110))
                self.add_widget(week4_label)
                self.labels.append(week4_label)
                month_label = MDLabel(text=self.selected_month, color=(0, 0, 0, 1), size_hint=(None, None),
                                    size=(40, 30),
                                    pos=(289,70))
                self.add_widget(month_label)
                self.labels.append(month_label)
                seat_label = MDLabel(text="Seat Occupied",color=(0, 0, 0, 1), size_hint=(None, None),
                                    size=(200, 30),pos=(210,400))
                self.add_widget(seat_label)
                self.labels.append(seat_label)


    def update_graph(self, new_data=None):
        """Update the graph with new data."""
        if new_data is not None:
            self.data = new_data  # Update the data list
        self.opacity = 1  # Make the graph visible
        self.clear_bars()
        self.draw_bars()

    def show(self):
        """Make the graph visible."""
        self.opacity = 1  # Set opacity to 1 to make the graph visible

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
            values=[f'{str(i).zfill(2)}:00-{str(i + 1).zfill(2)}:00' for i in range(9, 24)],
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


class Login_scr(MDScreen):
    pass
class Register_scr(MDScreen):
    pass

class User_Dashboard(MDScreen):
    pass

class Home_scr(MDScreen):
    pass
class Past_Analysis(MDScreen):
    pass
class Student_register(MDScreen):
    pass
class Future_Booking(MDScreen):
    pass

class Hall_selection(MDScreen):
    pass

class Seat_selection1(MDScreen):
    pass

class Account_setting(MDScreen):
    pass
class Seat_selection2(MDScreen):
    pass
class Delete_student_registration(MDScreen):
    pass

class AdminseatbookerApp(MDApp):
    dialog = None
    def build(self):
        self.theme_cls.primary_palette = "Amber"
        self.theme_cls.theme_style = "Dark"
        self.firebase_url = 'https://libraryseatbooking-37c44-default-rtdb.firebaseio.com/'
        self.executer = ThreadPoolExecutor(max_workers=6)
        self.bldr = Builder.load_file("Adminseatbooker.kv")
        self.executer.submit(self.load_scrs)
        self.bar_graph = self.bldr.get_screen("past_analysis").ids.bar_graph
        return self.bldr

   
    def load_scrs(self):
        sm = MDScreenManager()
        sm.add_widget(Home_scr(name="home"))
        sm.add_widget(Login_scr(name="login"))
        sm.add_widget(Register_scr(name="register"))
        sm.add_widget(User_Dashboard(name="user_dashboard"))
        sm.add_widget(Past_Analysis(name="past_analysis"))
        sm.add_widget(Student_register(name="student_register"))
        sm.add_widget(Delete_student_registration(name="student_delete_registration"))
        sm.add_widget(Future_Booking(name="future_booking"))
        sm.add_widget(Hall_selection(name="hall_selection"))
        sm.add_widget(Seat_selection1(name="seat_selection1"))
        sm.add_widget(Seat_selection2(name="seat_selection2"))
        sm.add_widget(Account_setting(name="account_setting"))

    def on_start(self):

        self.bldr.get_screen("hall_selection").ids.container.add_widget(
            OneLineListItem(
                text="UG Hall",
                on_release=lambda x: self.seatselection("UG Hall")
            )
        )
        self.bldr.get_screen("hall_selection").ids.container.add_widget(
            OneLineListItem(
                text="PG Hall",
                on_release=lambda i: self.seatselection("PG Hall")
            )
        )

    def on_stop(self):
        self.executer.shutdown(wait=True)

    def switch_to_register(self):
        self.root.current = "register"

    def switch_to_past_analysis(self):
        self.bar_graph.clear_bars()
        self.root.current = "past_analysis"

    def switch_to_login(self):
        self.root.current = "login"

    def switch_to_account_setting(self):
        self.root.current = "account_setting"

    def switch_to_hall_selection(self):
        self.root.current = "hall_selection"
    def switch_to_future_booking(self):
        self.root.current = "future_booking"

    def switch_to_home(self):
        self.root.current = "home"

    def switch_to_user_dashboard(self):
        self.root.current = "user_dashboard"

    def switch_to_student_register(self):
        self.root.current = "student_register"

    def switch_to_student_delete_registration(self):
        self.root.current = "student_delete_registration"

    def switch_to_seat_selection1(self):
        self.root.current = "seat_selection1"

    def switch_to_seat_selection2(self):
        self.root.current = "seat_selection2"

    def from_on_time_selected(self, selected_time1):
        self.from_selected_time = dt.datetime.strptime(selected_time1, "%H:%M").time()

    def to_on_time_selected(self, selected_time2):
        self.to_selected_time = dt.datetime.strptime(selected_time2, "%H:%M").time()

    def get_data(self):
        self.username = self.bldr.get_screen("login").ids.username.text
        self.password = self.bldr.get_screen("login").ids.passwd.text
        self.check_user()

    def check_user(self):
        path="admin_details"
        url=f"{self.firebase_url}/{path}.json"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                admin_data = response.json()
                if isinstance(admin_data, list):
                    validated_user = None
                    for user_details in admin_data:
                        if isinstance(user_details, dict):
                            username = user_details.get('USERNAME')
                            fullname = user_details.get('FULLNAME')
                            password = user_details.get('PASSWORD')
                            if username is not None and password is not None:
                                if username == str(self.username).upper() and password == str(self.password):
                                    # Set validated_user to the username and password only
                                    validated_user = {
                                        "USERNAME": username,
                                        "PASSWORD": password,
                                        "FULLNAME": fullname
                                    }
                                    break  # Exit loop when a match is found


                    if validated_user:
                        self.bldr.get_screen("user_dashboard").ids.name.text = f"Welcome {validated_user['FULLNAME']}"
                        self.bldr.get_screen("user_dashboard").ids.name1.text = f"Name: {validated_user['FULLNAME']}"
                        self.bldr.get_screen("user_dashboard").ids.header_title.text = validated_user["FULLNAME"]
                        self.switch_to_user_dashboard()
                    else:
                        self.show_error_dialog("Please check your username or password")

                else:
                    self.show_error_dialog("User does not exist")

            else:
                self.show_error_dialog(f"Error: {response.status_code}, {response.text}")
        except Exception as e:
            self.show_error_dialog(f"Failed to Connect because : {e}")

    def get_admin_data(self):
        self.admin_fullname = self.bldr.get_screen("register").ids.admin_fullname.text
        self.admin_email = self.bldr.get_screen("register").ids.admin_email.text
        self.admin_username = self.bldr.get_screen("register").ids.admin_username.text
        self.admin_new_passwd = self.bldr.get_screen("register").ids.admin_new_passwd.text
        self.admin_confirm_passwd = self.bldr.get_screen("register").ids.admin_confirm_passwd.text
        self.check_admin_and_register()
    def check_admin_and_register(self):
        path="admin_details"
        url=f"{self.firebase_url}/{path}.json"
        try:
            response= requests.get(url)
            if response.status_code == 200 :
                admin_data = response.json()
                if isinstance(admin_data, list):
                    validated_user = None
                    for user_details in admin_data:
                        if isinstance(user_details, dict):
                            username = user_details.get('USERNAME')
                            if username is not None:
                                if username == str(self.admin_username).upper() :
                                    # Set validated_user to the username and password only
                                    validated_user = {
                                        "USERNAME": username
                                    }
                                    break  # Exit loop when a match is found


                    if validated_user:
                        self.show_error_dialog(f"Please go to login page")

                    else:
                        if self.admin_fullname and self.admin_email and self.admin_username and self.admin_new_passwd and self.admin_confirm_passwd is not None:
                            if self.admin_new_passwd == self.admin_confirm_passwd:
                                admin_data1 = {
                                    "FULLNAME": str(self.admin_fullname).upper(),
                                    "EMAIL": str(self.admin_email),
                                    "USERNAME": str(self.admin_username).upper(),
                                    "PASSWORD": str(self.admin_confirm_passwd)
                                }
                                upcoming_id = []
                                if admin_data is not None:
                                    for id1, details in enumerate(admin_data):
                                        upcoming_id.append(id1)
                                    next_id = max(upcoming_id) + 1
                                else:
                                    next_id = 1
                                try:
                                    response1 = requests.patch(f"{self.firebase_url}/{path}/{next_id}.json",
                                                             json=admin_data1)
                                    if response1.status_code == 200:
                                        self.show_error_dialog("Registered, Successfully. Now please go to login page")
                                    else:
                                        self.show_error_dialog(f"Unable to register: {response1.status_code}, {response1.text}")
                                except Exception as e:
                                    self.show_error_dialog(f"Error {e}")
                            else:
                                self.show_error_dialog("New Password and Confirm Password should be same")
                        else:
                            self.show_error_dialog("No Field should be empty")

                else:
                    if self.admin_new_passwd == self.admin_confirm_passwd:
                        admin_data1 = {
                            "FULLNAME": str(self.admin_fullname).upper(),
                            "EMAIL": str(self.admin_email),
                            "USERNAME": str(self.admin_username).upper(),
                            "PASSWORD": str(self.admin_confirm_passwd)
                        }
                        next_id = 1
                        try:
                            response2 = requests.patch(f"{self.firebase_url}/{path}/{next_id}.json",
                                                       json=admin_data1)
                            if response2.status_code == 200:
                                self.show_error_dialog("Registered, Successfully. Now please go to login page")
                            else:
                                self.show_error_dialog(f"Unable to register: {response2.status_code}, {response2.text}")
                        except Exception as e:
                            self.show_error_dialog(f"Error {e}")
                    else:
                        self.show_error_dialog("New Password and Confirm Password should be same !")

            else:
                self.show_error_dialog(f"Error: {response.status_code}, {response.text}")
        except Exception as e:
            self.show_error_dialog(f"Error {e}")


    def show_year_menu(self, instance):
        # Define the items for the year dropdown menu
        menu_items = [
            {
                "text": year,
                "on_release": lambda x=year: self.year_item_selected(x)
            }
            for year in ['2024', '2025','2026','2027','2028']
        ]

        # Create and open the year dropdown menu
        self.year_menu = MDDropdownMenu(
            caller=instance,
            items=menu_items,
            width_mult=4
        )
        self.year_menu.open()

    def show_month_menu(self, instance):
        # Define the items for the month dropdown menu
        months = [
        ("Jan", 1), ("Feb", 2), ("Mar", 3), ("Apr", 4),
        ("May", 5), ("Jun", 6), ("Jul", 7), ("Aug", 8),
        ("Sep", 9), ("Oct", 10), ("Nov", 11), ("Dec", 12)
            ]
        menu_items = [
            {
                "text": f"{month}",  # Display name and number
                "on_release": lambda x=(month, num): self.month_item_selected(x)
            }
            for month, num in months
        ]

        # Create and open the month dropdown menu
        self.month_menu = MDDropdownMenu(
            caller=instance,
            items=menu_items,
            width_mult=4
        )
        self.month_menu.open()

    def year_item_selected(self, year1):
        self.year_menu.dismiss()
        current_year = dt.datetime.now().year
        if str(current_year)>=str(year1):
            self.year = year1
        else:
            self.show_error_dialog("Please Select the Current or Previous Year")
        self.bldr.get_screen("past_analysis").ids.year_label.text = f"Selected Year: {year1}"

    def month_item_selected(self, month_tuple):
        self.month_menu.dismiss()
        month_name, month_num = month_tuple
        current_mon_year = dt.datetime.now().strftime("%Y-%m")
        user_date = (self.year,month_num)
        if str(current_mon_year)>=str(user_date):
            self.month_num = month_num
            self.month_name = month_name
        else:
            self.show_error_dialog("Please Select Month and Year before Current Date")
        self.bldr.get_screen("past_analysis").ids.month_label.text = f"Selected Month: {month_name}"
    def update_graph(self):
        self.bar_plot = BarGraphWidget()
        path = "Past_booking"
        url = f"{self.firebase_url}/{path}.json"
        categorized_data = {}
        weekly_counts = {}
        try:
            response = requests.get(url)
            if response.status_code == 200:
                existing_data = response.json()
                if isinstance(existing_data,list):
                    for past_data in existing_data:
                        if isinstance(past_data,dict):
                            record_date = dt.datetime.strptime(past_data["date"], "%d-%m-%Y")
                            year, month, day = record_date.year, record_date.month, record_date.day
                            _, total_days = monthrange(year, month)
                            week1_end = min(7, total_days)
                            week2_end = min(14, total_days)
                            week3_end = min(21, total_days)
                            week4_end = total_days

                            # Categorize based on day
                            if 1 <= day <= week1_end:
                                week = "Week1"
                            elif week1_end < day <= week2_end:
                                week = "Week2"
                            elif week2_end < day <= week3_end:
                                week = "Week3"
                            elif week3_end < day <= week4_end:
                                week = "Week4"
                            else:
                                continue
                            if week not in categorized_data:
                                categorized_data[week] = []

                            if str(self.month_num) == str(month) and str(self.year) == str(year):
                                categorized_data[week].append(past_data)
                                weekly_counts[week] = weekly_counts.get(week, 0) + 1


        except Exception as e:
            self.show_error_dialog(f"Error{e}")
        try:
            self.bar_graph.set_data(self.year,self.month_name,weekly_counts)
            self.bar_graph.clear_bars()
            self.bar_graph.update_graph()
        except AttributeError as e:
            self.show_error_dialog(f"Please Select Year and Month {e}")

    def get_student_data(self):
        self.student_fullname = self.bldr.get_screen("student_register").ids.student_fullname.text
        self.student_email = self.bldr.get_screen("student_register").ids.student_email.text
        self.student_username = self.bldr.get_screen("student_register").ids.student_username.text
        self.student_new_passwd = self.bldr.get_screen("student_register").ids.student_new_passwd.text
        self.student_confirm_passwd = self.bldr.get_screen("student_register").ids.student_confirm_passwd.text
        self.check_student_and_register()
    def check_student_and_register(self):
        path = 'student_details'
        url = f'{self.firebase_url}/{path}'
        try:
            response = requests.get(f"{url}.json")
            if response.status_code == 200 :
                student_data = response.json()
                if isinstance(student_data, list):
                    validated_user = None
                    for user_details in student_data:
                        if isinstance(user_details, dict):
                            username = user_details.get('USERNAME')
                            if username is not None:
                                if username == str(self.student_username).upper() :
                                    # Set validated_user to the username and password only
                                    validated_user = {
                                        "USERNAME": username
                                    }
                                    break  # Exit loop when a match is found


                    if validated_user:
                        self.show_error_dialog(f"Student has already been register!")

                    else:
                        if self.student_new_passwd == self.student_confirm_passwd:
                            student_data1 = {
                                "FULLNAME": str(self.student_fullname).upper(),
                                "EMAIL": str(self.student_email),
                                "USERNAME": str(self.student_username).upper(),
                                "PASSWORD": str(self.student_confirm_passwd)
                            }
                            upcoming_id = []
                            if student_data is not None:
                                for id1, details in enumerate(student_data):
                                    upcoming_id.append(id1)
                                next_id = max(upcoming_id) + 1
                            else:
                                next_id = 1
                            try:
                                response1 = requests.patch(f"{url}/{next_id}.json",
                                                         json=student_data1)
                                if response1.status_code == 200:
                                    self.show_error_dialog("Student Registered Successfully")
                                else:
                                    self.show_error_dialog("Unable to register!")
                            except Exception as e:
                                self.show_error_dialog(f"Error {e}")
                        else:
                            self.show_error_dialog("New password and confirm password should be same")
                else:
                    if self.student_new_passwd == self.student_confirm_passwd:
                        student_data1 = {
                            "FULLNAME": str(self.student_fullname).upper(),
                            "EMAIL": str(self.student_email),
                            "USERNAME": str(self.student_username).upper(),
                            "PASSWORD": str(self.student_confirm_passwd)
                        }
                        next_id = 1
                        try:
                            response2 = requests.patch(f"{url}/{next_id}.json",
                                                       json=student_data1)
                            if response2.status_code == 200:
                                self.show_error_dialog("Student Registered Successfully")
                            else:
                                self.show_error_dialog("Unable to register!")
                        except Exception as e:
                            self.show_error_dialog(f"Error {e}")
                    else:
                        self.show_error_dialog("New Password and Confirm Password should be same!")
            else:
                self.show_error_dialog(f"Error: {response.status_code}, {response.text}")


        except Exception as e:
            self.show_error_dialog(f"Error {e}")

    def delete_registration(self):
        student_delete_username = self.bldr.get_screen("student_delete_registration").ids.delete_student_username.text
        path = 'student_details'
        url = f'{self.firebase_url}/{path}'
        try:
            response = requests.get(f"{url}.json")
            if response.status_code == 200:
                student_data = response.json()
                if isinstance(student_data,list):
                    for id1, student_details in enumerate(student_data):
                        if isinstance(student_details,dict):
                            student_username = student_details.get("USERNAME")
                            if str(student_username) == str(student_delete_username).upper():
                                try:
                                    response1 = requests.delete(f"{url}/{id1}.json")
                                    if response1.status_code == 200:
                                        self.show_error_dialog("Student Registration Successfully Deleted!")
                                except Exception as e:
                                    self.show_error_dialog(f"Error {e}")
                            else:
                               self.show_error_dialog("Student Not Found!,Please try again enter the correct student username")
        except Exception as e:
            self.show_error_dialog(f"Error {e}")
    def hello_print(self,*args):
        pass
    def future_booking(self):
        self.bldr.get_screen("future_booking").ids.Future_booking.clear_widgets()
        path = "Upcoming_Booking"
        url = f"{self.firebase_url}/{path}"
        try:
            response = requests.get(f"{url}.json")
            if response.status_code == 200:
                future_booking = response.json()
                if isinstance(future_booking,list):
                    for details in future_booking:
                        if isinstance(details,dict):
                            seat_no = details.get("seat_no")
                            seat_date = details.get("date")
                            seat_from_time = details.get("from_time")
                            seat_to_time = details.get("to_time")
                            seat_booked_by = details.get("booked_by")
                            list_item = ThreeLineIconListItem(
                                text=f"Seat No: {seat_no} ",
                                secondary_text=f"Date: {seat_date} \n Booked By: {seat_booked_by}",
                                tertiary_text=f"From Time: {seat_from_time} \n To Time: {seat_to_time}",
                                on_release=lambda x, seat_no1=seat_no, seat_booked_by1=seat_booked_by: self.on_click(
                                    seat_no1, seat_booked_by1, list_item)
                            )
                            icon = IconLeftWidget(icon="calendar-check")
                            list_item.add_widget(icon)
                            self.bldr.get_screen("future_booking").ids.Future_booking.add_widget(list_item)
        except Exception as e:
            self.show_error_dialog(f"Error {e}")
        self.switch_to_future_booking()

    def on_click(self,seat_no,seat_booked_by,list_item):
        self.dialog4 = MDDialog(
            title="Cancel Booking",
            text="Are you sure you want to cancel your booking?",
            buttons=[
                MDRaisedButton(
                    text="Yes",
                    on_release=lambda x: self.confirm_cancel(seat_booked_by, seat_no, list_item)
                ),
                MDRaisedButton(
                    text="No",
                    on_release=lambda _: self.dialog4.dismiss()
                ),
            ],
        )
        self.dialog4.open()
    def confirm_cancel(self,seat_booked_by,seat_no,list_item):
        path = "Upcoming_Booking"
        url = f"{self.firebase_url}/{path}"
        self.bldr.get_screen("future_booking").ids.Future_booking.remove_widget(list_item)
        self.dialog4.dismiss()
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
                                        self.future_booking()
                                except Exception as e:
                                    self.show_error_dialog(f"Error {e}")
                                hall_path = "hall_A_seat_details"
                                hall_url = f"{self.firebase_url}/{hall_path}"
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
        except Exception as e :
            self.show_error_dialog(f"Error {e}")
    def seatselection(self,other):
        if (other == "UG Hall"):
            self.switch_to_seat_selection1()
        elif (other == "PG Hall"):
            self.switch_to_seat_selection2()
        else:
            self.show_error_dialog("Please Select the hall number")

    def check_and_update(self):
        old_paaswd = self.bldr.get_screen("account_setting").ids.old_passwd.text
        new_paaswd = self.bldr.get_screen("account_setting").ids.new_passwd.text
        confirm_paaswd = self.bldr.get_screen("account_setting").ids.con_passwd.text
        path = 'admin_details'
        url = f'{self.firebase_url}/{path}'
        try:
            response = requests.get(f"{url}.json")
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
                                if username == self.username.upper() and str(password) == str(old_paaswd):
                                    validated_user = {
                                        "USERNAME": username,
                                        "PASSWORD": password
                                    }
                                    user_id = user_id_key  # Store user_id for updating password
                                    break
                    if validated_user and user_id:
                        update_url = f"{url}/{user_id}.json"
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

    def check_status(self):
        date_select = MDDatePicker(min_date=dt.date.today())
        date_select.bind(on_save=self.on_date_selected, on_cancel=self.on_cancel)
        date_select.open()
        self.time_picker = TimePickerDialog()

    def on_date_selected(self, instance, value, date_range):
        if str(value) < dt.datetime.today().strftime("%Y-%m-%d"):
            self.show_error_dialog("Please select the date of today or in future")
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
        formatted_time = current_time.strftime("%d-%m-%Y %H:%M:%S")
        try:
            response = requests.get(url)
            if response.status_code == 200:
                upcomming_data = response.json()

                if isinstance(upcomming_data, list):
                    for upcoming_details in upcomming_data:
                        if isinstance(upcoming_details, dict):
                            booked_by = upcoming_details.get("booked_by")
                            up_date = upcoming_details.get("date")
                            from_time = upcoming_details.get("from_time")
                            to_time = upcoming_details.get("to_time")
                            seat_no = upcoming_details.get("seat_no")
                            if (str(up_date) == str(formatted_date) and str(from_time) == str(
                                    self.from_selected_time) and str(self.to_selected_time) == str(
                                    to_time) and booked_by != None):
                                if self.bldr.get_screen("seat_selection1").ids.seat1.name == seat_no:
                                    self.bldr.get_screen("seat_selection1").ids.seat1.disabled = True
                                elif self.bldr.get_screen("seat_selection1").ids.seat2.name == seat_no:
                                    self.bldr.get_screen("seat_selection1").ids.seat2.disabled = True
                                elif self.bldr.get_screen("seat_selection1").ids.seat3.name == seat_no:
                                    self.bldr.get_screen("seat_selection1").ids.seat3.disabled = True
                                elif self.bldr.get_screen("seat_selection1").ids.seat4.name == seat_no:
                                    self.bldr.get_screen("seat_selection1").ids.seat4.disabled = True
                                elif self.bldr.get_screen("seat_selection1").ids.seat5.name == seat_no:
                                    self.bldr.get_screen("seat_selection1").ids.seat5.disabled = True
                                elif self.bldr.get_screen("seat_selection1").ids.seat6.name == seat_no:
                                    self.bldr.get_screen("seat_selection1").ids.seat6.disabled = True
                                elif self.bldr.get_screen("seat_selection1").ids.seat7.name == seat_no:
                                    self.bldr.get_screen("seat_selection1").ids.seat7.disabled = True
                                elif self.bldr.get_screen("seat_selection1").ids.seat8.name == seat_no:
                                    self.bldr.get_screen("seat_selection1").ids.seat8.disabled = True
                                elif self.bldr.get_screen("seat_selection1").ids.seat9.name == seat_no:
                                    self.bldr.get_screen("seat_selection1").ids.seat9.disabled = True
                                elif self.bldr.get_screen("seat_selection1").ids.seat10.name == seat_no:
                                    self.bldr.get_screen("seat_selection1").ids.seat10.disabled = True
                                elif self.bldr.get_screen("seat_selection1").ids.seat11.name == seat_no:
                                    self.bldr.get_screen("seat_selection1").ids.seat11.disabled = True
                                elif self.bldr.get_screen("seat_selection1").ids.seat12.name == seat_no:
                                    self.bldr.get_screen("seat_selection1").ids.seat12.disabled = True
                                elif self.bldr.get_screen("seat_selection1").ids.seat13.name == seat_no:
                                    self.bldr.get_screen("seat_selection1").ids.seat13.disabled = True
                                elif self.bldr.get_screen("seat_selection1").ids.seat14.name == seat_no:
                                    self.bldr.get_screen("seat_selection1").ids.seat14.disabled = True
                                elif self.bldr.get_screen("seat_selection1").ids.seat15.name == seat_no:
                                    self.bldr.get_screen("seat_selection1").ids.seat15.disabled = True
                                elif self.bldr.get_screen("seat_selection1").ids.seat16.name == seat_no:
                                    self.bldr.get_screen("seat_selection1").ids.seat16.disabled = True
                                elif self.bldr.get_screen("seat_selection1").ids.seat17.name == seat_no:
                                    self.bldr.get_screen("seat_selection1").ids.seat17.disabled = True
                                elif self.bldr.get_screen("seat_selection1").ids.seat18.name == seat_no:
                                    self.bldr.get_screen("seat_selection1").ids.seat18.disabled = True
                                elif self.bldr.get_screen("seat_selection1").ids.seat19.name == seat_no:
                                    self.bldr.get_screen("seat_selection1").ids.seat19.disabled = True
                                elif self.bldr.get_screen("seat_selection1").ids.seat20.name == seat_no:
                                    self.bldr.get_screen("seat_selection1").ids.seat20.disabled = True
                                elif self.bldr.get_screen("seat_selection1").ids.seat21.name == seat_no:
                                    self.bldr.get_screen("seat_selection1").ids.seat21.disabled = True
                                elif self.bldr.get_screen("seat_selection1").ids.seat22.name == seat_no:
                                    self.bldr.get_screen("seat_selection1").ids.seat22.disabled = True
                                elif self.bldr.get_screen("seat_selection1").ids.seat23.name == seat_no:
                                    self.bldr.get_screen("seat_selection1").ids.seat23.disabled = True
                                elif self.bldr.get_screen("seat_selection1").ids.seat24.name == seat_no:
                                    self.bldr.get_screen("seat_selection1").ids.seat24.disabled = True
                                elif self.bldr.get_screen("seat_selection1").ids.seat25.name == seat_no:
                                    self.bldr.get_screen("seat_selection1").ids.seat25.disabled = True
                                elif self.bldr.get_screen("seat_selection1").ids.seat26.name == seat_no:
                                    self.bldr.get_screen("seat_selection1").ids.seat26.disabled = True
                                elif self.bldr.get_screen("seat_selection1").ids.seat27.name == seat_no:
                                    self.bldr.get_screen("seat_selection1").ids.seat27.disabled = True
                                elif self.bldr.get_screen("seat_selection1").ids.seat28.name == seat_no:
                                    self.bldr.get_screen("seat_selection1").ids.seat28.disabled = True
                                elif self.bldr.get_screen("seat_selection1").ids.seat29.name == seat_no:
                                    self.bldr.get_screen("seat_selection1").ids.seat29.disabled = True
                                elif self.bldr.get_screen("seat_selection1").ids.seat30.name == seat_no:
                                    self.bldr.get_screen("seat_selection1").ids.seat30.disabled = True
                                elif self.bldr.get_screen("seat_selection1").ids.seat31.name == seat_no:
                                    self.bldr.get_screen("seat_selection1").ids.seat31.disabled = True
                                elif self.bldr.get_screen("seat_selection1").ids.seat32.name == seat_no:
                                    self.bldr.get_screen("seat_selection1").ids.seat32.disabled = True
                                elif self.bldr.get_screen("seat_selection1").ids.seat33.name == seat_no:
                                    self.bldr.get_screen("seat_selection1").ids.seat33.disabled = True
                                elif self.bldr.get_screen("seat_selection1").ids.seat34.name == seat_no:
                                    self.bldr.get_screen("seat_selection1").ids.seat34.disabled = True
                                elif self.bldr.get_screen("seat_selection1").ids.seat35.name == seat_no:
                                    self.bldr.get_screen("seat_selection1").ids.seat35.disabled = True
                                elif self.bldr.get_screen("seat_selection1").ids.seat36.name == seat_no:
                                    self.bldr.get_screen("seat_selection1").ids.seat36.disabled = True
                                elif self.bldr.get_screen("seat_selection1").ids.seat37.name == seat_no:
                                    self.bldr.get_screen("seat_selection1").ids.seat37.disabled = True
                                elif self.bldr.get_screen("seat_selection1").ids.seat38.name == seat_no:
                                    self.bldr.get_screen("seat_selection1").ids.seat38.disabled = True
                                elif self.bldr.get_screen("seat_selection1").ids.seat39.name == seat_no:
                                    self.bldr.get_screen("seat_selection1").ids.seat39.disabled = True
                                elif self.bldr.get_screen("seat_selection1").ids.seat40.name == seat_no:
                                    self.bldr.get_screen("seat_selection1").ids.seat40.disabled = True
                                elif self.bldr.get_screen("seat_selection1").ids.seat41.name == seat_no:
                                    self.bldr.get_screen("seat_selection1").ids.seat41.disabled = True
                                elif self.bldr.get_screen("seat_selection1").ids.seat42.name == seat_no:
                                    self.bldr.get_screen("seat_selection1").ids.seat42.disabled = True
                                elif self.bldr.get_screen("seat_selection1").ids.seat43.name == seat_no:
                                    self.bldr.get_screen("seat_selection1").ids.seat43.disabled = True
                                elif self.bldr.get_screen("seat_selection1").ids.seat44.name == seat_no:
                                    self.bldr.get_screen("seat_selection1").ids.seat44.disabled = True
                                elif self.bldr.get_screen("seat_selection1").ids.seat45.name == seat_no:
                                    self.bldr.get_screen("seat_selection1").ids.seat45.disabled = True
                                elif self.bldr.get_screen("seat_selection1").ids.seat46.name == seat_no:
                                    self.bldr.get_screen("seat_selection1").ids.seat46.disabled = True
                                elif self.bldr.get_screen("seat_selection1").ids.seat47.name == seat_no:
                                    self.bldr.get_screen("seat_selection1").ids.seat47.disabled = True
                                elif self.bldr.get_screen("seat_selection1").ids.seat48.name == seat_no:
                                    self.bldr.get_screen("seat_selection1").ids.seat48.disabled = True
                                elif self.bldr.get_screen("seat_selection1").ids.seat49.name == seat_no:
                                    self.bldr.get_screen("seat_selection1").ids.seat49.disabled = True
                                elif self.bldr.get_screen("seat_selection1").ids.seat50.name == seat_no:
                                    self.bldr.get_screen("seat_selection1").ids.seat50.disabled = True
                                elif self.bldr.get_screen("seat_selection1").ids.seat51.name == seat_no:
                                    self.bldr.get_screen("seat_selection1").ids.seat51.disabled = True
                                elif self.bldr.get_screen("seat_selection1").ids.seat52.name == seat_no:
                                    self.bldr.get_screen("seat_selection1").ids.seat52.disabled = True
                                elif self.bldr.get_screen("seat_selection1").ids.seat53.name == seat_no:
                                    self.bldr.get_screen("seat_selection1").ids.seat53.disabled = True
                                elif self.bldr.get_screen("seat_selection1").ids.seat54.name == seat_no:
                                    self.bldr.get_screen("seat_selection1").ids.seat54.disabled = True
                                elif self.bldr.get_screen("seat_selection1").ids.seat55.name == seat_no:
                                    self.bldr.get_screen("seat_selection1").ids.seat55.disabled = True
                                elif self.bldr.get_screen("seat_selection1").ids.seat56.name == seat_no:
                                    self.bldr.get_screen("seat_selection1").ids.seat56.disabled = True
                                elif self.bldr.get_screen("seat_selection1").ids.seat57.name == seat_no:
                                    self.bldr.get_screen("seat_selection1").ids.seat57.disabled = True
                                elif self.bldr.get_screen("seat_selection1").ids.seat58.name == seat_no:
                                    self.bldr.get_screen("seat_selection1").ids.seat58.disabled = True
                                elif self.bldr.get_screen("seat_selection1").ids.seat59.name == seat_no:
                                    self.bldr.get_screen("seat_selection1").ids.seat59.disabled = True
                                elif self.bldr.get_screen("seat_selection1").ids.seat60.name == seat_no:
                                    self.bldr.get_screen("seat_selection1").ids.seat60.disabled = True
                                elif self.bldr.get_screen("seat_selection1").ids.seat61.name == seat_no:
                                    self.bldr.get_screen("seat_selection1").ids.seat61.disabled = True
                                elif self.bldr.get_screen("seat_selection1").ids.seat62.name == seat_no:
                                    self.bldr.get_screen("seat_selection1").ids.seat62.disabled = True
                                elif self.bldr.get_screen("seat_selection1").ids.seat63.name == seat_no:
                                    self.bldr.get_screen("seat_selection1").ids.seat63.disabled = True
                                elif self.bldr.get_screen("seat_selection1").ids.seat64.name == seat_no:
                                    self.bldr.get_screen("seat_selection1").ids.seat64.disabled = True
                                elif self.bldr.get_screen("seat_selection1").ids.seat65.name == seat_no:
                                    self.bldr.get_screen("seat_selection1").ids.seat65.disabled = True
                                elif self.bldr.get_screen("seat_selection1").ids.seat66.name == seat_no:
                                    self.bldr.get_screen("seat_selection1").ids.seat66.disabled = True
                                elif self.bldr.get_screen("seat_selection1").ids.seat67.name == seat_no:
                                    self.bldr.get_screen("seat_selection1").ids.seat67.disabled = True
                                elif self.bldr.get_screen("seat_selection1").ids.seat68.name == seat_no:
                                    self.bldr.get_screen("seat_selection1").ids.seat68.disabled = True
                                elif self.bldr.get_screen("seat_selection1").ids.seat69.name == seat_no:
                                    self.bldr.get_screen("seat_selection1").ids.seat69.disabled = True
                                elif self.bldr.get_screen("seat_selection1").ids.seat70.name == seat_no:
                                    self.bldr.get_screen("seat_selection1").ids.seat70.disabled = True
                                elif self.bldr.get_screen("seat_selection1").ids.seat71.name == seat_no:
                                    self.bldr.get_screen("seat_selection1").ids.seat71.disabled = True
                                elif self.bldr.get_screen("seat_selection1").ids.seat72.name == seat_no:
                                    self.bldr.get_screen("seat_selection1").ids.seat72.disabled = True
                                elif self.bldr.get_screen("seat_selection1").ids.seat73.name == seat_no:
                                    self.bldr.get_screen("seat_selection1").ids.seat73.disabled = True
                                elif self.bldr.get_screen("seat_selection1").ids.seat74.name == seat_no:
                                    self.bldr.get_screen("seat_selection1").ids.seat74.disabled = True
                                elif self.bldr.get_screen("seat_selection1").ids.seat75.name == seat_no:
                                    self.bldr.get_screen("seat_selection1").ids.seat75.disabled = True
                                elif self.bldr.get_screen("seat_selection1").ids.seat76.name == seat_no:
                                    self.bldr.get_screen("seat_selection1").ids.seat76.disabled = True
                                elif self.bldr.get_screen("seat_selection1").ids.seat77.name == seat_no:
                                    self.bldr.get_screen("seat_selection1").ids.seat77.disabled = True
                                elif self.bldr.get_screen("seat_selection1").ids.seat78.name == seat_no:
                                    self.bldr.get_screen("seat_selection1").ids.seat78.disabled = True
                                elif self.bldr.get_screen("seat_selection1").ids.seat79.name == seat_no:
                                    self.bldr.get_screen("seat_selection1").ids.seat79.disabled = True
                                elif self.bldr.get_screen("seat_selection1").ids.seat80.name == seat_no:
                                    self.bldr.get_screen("seat_selection1").ids.seat80.disabled = True
                                elif self.bldr.get_screen("seat_selection1").ids.seat81.name == seat_no:
                                    self.bldr.get_screen("seat_selection1").ids.seat81.disabled = True
                                elif self.bldr.get_screen("seat_selection1").ids.seat82.name == seat_no:
                                    self.bldr.get_screen("seat_selection1").ids.seat82.disabled = True
                                elif self.bldr.get_screen("seat_selection1").ids.seat83.name == seat_no:
                                    self.bldr.get_screen("seat_selection1").ids.seat83.disabled = True
                                elif self.bldr.get_screen("seat_selection1").ids.seat84.name == seat_no:
                                    self.bldr.get_screen("seat_selection1").ids.seat84.disabled = True
                            else:
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

                if isinstance(upcomming_data, list):
                    for upcoming_details in upcomming_data:
                        if isinstance(upcoming_details, dict):
                            booked_by = upcoming_details.get("booked_by")
                            up_date = upcoming_details.get("date")
                            from_time = upcoming_details.get("from_time")
                            to_time = upcoming_details.get("to_time")
                            seat_no = upcoming_details.get("seat_no")
                            if (str(up_date) == str(formatted_date) and str(from_time) == str(
                                    self.from_selected_time) and str(self.to_selected_time) == str(
                                    to_time) and booked_by != None):
                                if self.bldr.get_screen("seat_selection2").ids.seat1.name == seat_no:
                                    self.bldr.get_screen("seat_selection2").ids.seat1.disabled = True
                                elif self.bldr.get_screen("seat_selection2").ids.seat2.name == seat_no:
                                    self.bldr.get_screen("seat_selection2").ids.seat2.disabled = True
                                elif self.bldr.get_screen("seat_selection2").ids.seat3.name == seat_no:
                                    self.bldr.get_screen("seat_selection2").ids.seat3.disabled = True
                                elif self.bldr.get_screen("seat_selection2").ids.seat4.name == seat_no:
                                    self.bldr.get_screen("seat_selection2").ids.seat4.disabled = True
                                elif self.bldr.get_screen("seat_selection2").ids.seat5.name == seat_no:
                                    self.bldr.get_screen("seat_selection2").ids.seat5.disabled = True
                                elif self.bldr.get_screen("seat_selection2").ids.seat6.name == seat_no:
                                    self.bldr.get_screen("seat_selection2").ids.seat6.disabled = True
                                elif self.bldr.get_screen("seat_selection2").ids.seat7.name == seat_no:
                                    self.bldr.get_screen("seat_selection2").ids.seat7.disabled = True
                                elif self.bldr.get_screen("seat_selection2").ids.seat8.name == seat_no:
                                    self.bldr.get_screen("seat_selection2").ids.seat8.disabled = True
                                elif self.bldr.get_screen("seat_selection2").ids.seat9.name == seat_no:
                                    self.bldr.get_screen("seat_selection2").ids.seat9.disabled = True
                                elif self.bldr.get_screen("seat_selection2").ids.seat10.name == seat_no:
                                    self.bldr.get_screen("seat_selection2").ids.seat10.disabled = True
                                elif self.bldr.get_screen("seat_selection2").ids.seat11.name == seat_no:
                                    self.bldr.get_screen("seat_selection2").ids.seat11.disabled = True
                                elif self.bldr.get_screen("seat_selection2").ids.seat12.name == seat_no:
                                    self.bldr.get_screen("seat_selection2").ids.seat12.disabled = True
                                elif self.bldr.get_screen("seat_selection2").ids.seat13.name == seat_no:
                                    self.bldr.get_screen("seat_selection2").ids.seat13.disabled = True
                                elif self.bldr.get_screen("seat_selection2").ids.seat14.name == seat_no:
                                    self.bldr.get_screen("seat_selection2").ids.seat14.disabled = True
                                elif self.bldr.get_screen("seat_selection2").ids.seat15.name == seat_no:
                                    self.bldr.get_screen("seat_selection2").ids.seat15.disabled = True
                                elif self.bldr.get_screen("seat_selection2").ids.seat16.name == seat_no:
                                    self.bldr.get_screen("seat_selection2").ids.seat16.disabled = True
                                elif self.bldr.get_screen("seat_selection2").ids.seat17.name == seat_no:
                                    self.bldr.get_screen("seat_selection2").ids.seat17.disabled = True
                                elif self.bldr.get_screen("seat_selection2").ids.seat18.name == seat_no:
                                    self.bldr.get_screen("seat_selection2").ids.seat18.disabled = True
                                elif self.bldr.get_screen("seat_selection2").ids.seat19.name == seat_no:
                                    self.bldr.get_screen("seat_selection2").ids.seat19.disabled = True
                                elif self.bldr.get_screen("seat_selection2").ids.seat20.name == seat_no:
                                    self.bldr.get_screen("seat_selection2").ids.seat20.disabled = True
                                elif self.bldr.get_screen("seat_selection2").ids.seat21.name == seat_no:
                                    self.bldr.get_screen("seat_selection2").ids.seat21.disabled = True
                                elif self.bldr.get_screen("seat_selection2").ids.seat22.name == seat_no:
                                    self.bldr.get_screen("seat_selection2").ids.seat22.disabled = True
                                elif self.bldr.get_screen("seat_selection2").ids.seat23.name == seat_no:
                                    self.bldr.get_screen("seat_selection2").ids.seat23.disabled = True
                                elif self.bldr.get_screen("seat_selection2").ids.seat24.name == seat_no:
                                    self.bldr.get_screen("seat_selection2").ids.seat24.disabled = True
                                elif self.bldr.get_screen("seat_selection2").ids.seat25.name == seat_no:
                                    self.bldr.get_screen("seat_selection2").ids.seat25.disabled = True
                                elif self.bldr.get_screen("seat_selection2").ids.seat26.name == seat_no:
                                    self.bldr.get_screen("seat_selection2").ids.seat26.disabled = True
                                elif self.bldr.get_screen("seat_selection2").ids.seat27.name == seat_no:
                                    self.bldr.get_screen("seat_selection2").ids.seat27.disabled = True
                                elif self.bldr.get_screen("seat_selection2").ids.seat28.name == seat_no:
                                    self.bldr.get_screen("seat_selection2").ids.seat28.disabled = True
                                elif self.bldr.get_screen("seat_selection2").ids.seat29.name == seat_no:
                                    self.bldr.get_screen("seat_selection2").ids.seat29.disabled = True
                                elif self.bldr.get_screen("seat_selection2").ids.seat30.name == seat_no:
                                    self.bldr.get_screen("seat_selection2").ids.seat30.disabled = True
                                elif self.bldr.get_screen("seat_selection2").ids.seat31.name == seat_no:
                                    self.bldr.get_screen("seat_selection2").ids.seat31.disabled = True
                                elif self.bldr.get_screen("seat_selection2").ids.seat32.name == seat_no:
                                    self.bldr.get_screen("seat_selection2").ids.seat32.disabled = True
                                elif self.bldr.get_screen("seat_selection2").ids.seat33.name == seat_no:
                                    self.bldr.get_screen("seat_selection2").ids.seat33.disabled = True
                                elif self.bldr.get_screen("seat_selection2").ids.seat34.name == seat_no:
                                    self.bldr.get_screen("seat_selection2").ids.seat34.disabled = True
                                elif self.bldr.get_screen("seat_selection2").ids.seat35.name == seat_no:
                                    self.bldr.get_screen("seat_selection2").ids.seat35.disabled = True
                                elif self.bldr.get_screen("seat_selection2").ids.seat36.name == seat_no:
                                    self.bldr.get_screen("seat_selection2").ids.seat36.disabled = True
                                elif self.bldr.get_screen("seat_selection2").ids.seat37.name == seat_no:
                                    self.bldr.get_screen("seat_selection2").ids.seat37.disabled = True
                                elif self.bldr.get_screen("seat_selection2").ids.seat38.name == seat_no:
                                    self.bldr.get_screen("seat_selection2").ids.seat38.disabled = True
                                elif self.bldr.get_screen("seat_selection2").ids.seat39.name == seat_no:
                                    self.bldr.get_screen("seat_selection2").ids.seat39.disabled = True
                                elif self.bldr.get_screen("seat_selection2").ids.seat40.name == seat_no:
                                    self.bldr.get_screen("seat_selection2").ids.seat40.disabled = True
                                elif self.bldr.get_screen("seat_selection2").ids.seat41.name == seat_no:
                                    self.bldr.get_screen("seat_selection2").ids.seat41.disabled = True
                                elif self.bldr.get_screen("seat_selection2").ids.seat42.name == seat_no:
                                    self.bldr.get_screen("seat_selection2").ids.seat42.disabled = True
                                elif self.bldr.get_screen("seat_selection2").ids.seat43.name == seat_no:
                                    self.bldr.get_screen("seat_selection2").ids.seat43.disabled = True
                                elif self.bldr.get_screen("seat_selection2").ids.seat44.name == seat_no:
                                    self.bldr.get_screen("seat_selection2").ids.seat44.disabled = True
                                elif self.bldr.get_screen("seat_selection2").ids.seat45.name == seat_no:
                                    self.bldr.get_screen("seat_selection2").ids.seat45.disabled = True
                                elif self.bldr.get_screen("seat_selection2").ids.seat46.name == seat_no:
                                    self.bldr.get_screen("seat_selection2").ids.seat46.disabled = True
                                elif self.bldr.get_screen("seat_selection2").ids.seat47.name == seat_no:
                                    self.bldr.get_screen("seat_selection2").ids.seat47.disabled = True
                                elif self.bldr.get_screen("seat_selection2").ids.seat48.name == seat_no:
                                    self.bldr.get_screen("seat_selection2").ids.seat48.disabled = True
                                elif self.bldr.get_screen("seat_selection2").ids.seat49.name == seat_no:
                                    self.bldr.get_screen("seat_selection2").ids.seat49.disabled = True
                                elif self.bldr.get_screen("seat_selection2").ids.seat50.name == seat_no:
                                    self.bldr.get_screen("seat_selection2").ids.seat50.disabled = True
                                elif self.bldr.get_screen("seat_selection2").ids.seat51.name == seat_no:
                                    self.bldr.get_screen("seat_selection2").ids.seat51.disabled = True
                                elif self.bldr.get_screen("seat_selection2").ids.seat52.name == seat_no:
                                    self.bldr.get_screen("seat_selection2").ids.seat52.disabled = True
                                elif self.bldr.get_screen("seat_selection2").ids.seat53.name == seat_no:
                                    self.bldr.get_screen("seat_selection2").ids.seat53.disabled = True
                                elif self.bldr.get_screen("seat_selection2").ids.seat54.name == seat_no:
                                    self.bldr.get_screen("seat_selection2").ids.seat54.disabled = True
                                elif self.bldr.get_screen("seat_selection2").ids.seat55.name == seat_no:
                                    self.bldr.get_screen("seat_selection2").ids.seat55.disabled = True
                                elif self.bldr.get_screen("seat_selection2").ids.seat56.name == seat_no:
                                    self.bldr.get_screen("seat_selection2").ids.seat56.disabled = True
                                elif self.bldr.get_screen("seat_selection2").ids.seat57.name == seat_no:
                                    self.bldr.get_screen("seat_selection2").ids.seat57.disabled = True
                                elif self.bldr.get_screen("seat_selection2").ids.seat58.name == seat_no:
                                    self.bldr.get_screen("seat_selection2").ids.seat58.disabled = True
                                elif self.bldr.get_screen("seat_selection2").ids.seat59.name == seat_no:
                                    self.bldr.get_screen("seat_selection2").ids.seat59.disabled = True
                                elif self.bldr.get_screen("seat_selection2").ids.seat60.name == seat_no:
                                    self.bldr.get_screen("seat_selection2").ids.seat60.disabled = True
                                elif self.bldr.get_screen("seat_selection2").ids.seat61.name == seat_no:
                                    self.bldr.get_screen("seat_selection2").ids.seat61.disabled = True
                                elif self.bldr.get_screen("seat_selection2").ids.seat62.name == seat_no:
                                    self.bldr.get_screen("seat_selection2").ids.seat62.disabled = True
                                elif self.bldr.get_screen("seat_selection2").ids.seat63.name == seat_no:
                                    self.bldr.get_screen("seat_selection2").ids.seat63.disabled = True
                                elif self.bldr.get_screen("seat_selection2").ids.seat64.name == seat_no:
                                    self.bldr.get_screen("seat_selection2").ids.seat64.disabled = True
                                elif self.bldr.get_screen("seat_selection2").ids.seat65.name == seat_no:
                                    self.bldr.get_screen("seat_selection2").ids.seat65.disabled = True
                                elif self.bldr.get_screen("seat_selection2").ids.seat66.name == seat_no:
                                    self.bldr.get_screen("seat_selection2").ids.seat66.disabled = True
                                elif self.bldr.get_screen("seat_selection2").ids.seat67.name == seat_no:
                                    self.bldr.get_screen("seat_selection2").ids.seat67.disabled = True
                                elif self.bldr.get_screen("seat_selection2").ids.seat68.name == seat_no:
                                    self.bldr.get_screen("seat_selection2").ids.seat68.disabled = True
                                elif self.bldr.get_screen("seat_selection2").ids.seat69.name == seat_no:
                                    self.bldr.get_screen("seat_selection2").ids.seat69.disabled = True
                                elif self.bldr.get_screen("seat_selection2").ids.seat70.name == seat_no:
                                    self.bldr.get_screen("seat_selection2").ids.seat70.disabled = True
                                elif self.bldr.get_screen("seat_selection2").ids.seat71.name == seat_no:
                                    self.bldr.get_screen("seat_selection2").ids.seat71.disabled = True
                                elif self.bldr.get_screen("seat_selection2").ids.seat72.name == seat_no:
                                    self.bldr.get_screen("seat_selection2").ids.seat72.disabled = True
                                elif self.bldr.get_screen("seat_selection2").ids.seat73.name == seat_no:
                                    self.bldr.get_screen("seat_selection2").ids.seat73.disabled = True
                                elif self.bldr.get_screen("seat_selection2").ids.seat74.name == seat_no:
                                    self.bldr.get_screen("seat_selection2").ids.seat74.disabled = True
                                elif self.bldr.get_screen("seat_selection2").ids.seat75.name == seat_no:
                                    self.bldr.get_screen("seat_selection2").ids.seat75.disabled = True
                                elif self.bldr.get_screen("seat_selection2").ids.seat76.name == seat_no:
                                    self.bldr.get_screen("seat_selection2").ids.seat76.disabled = True
                                elif self.bldr.get_screen("seat_selection2").ids.seat77.name == seat_no:
                                    self.bldr.get_screen("seat_selection2").ids.seat77.disabled = True
                                elif self.bldr.get_screen("seat_selection2").ids.seat78.name == seat_no:
                                    self.bldr.get_screen("seat_selection2").ids.seat78.disabled = True
                                elif self.bldr.get_screen("seat_selection2").ids.seat79.name == seat_no:
                                    self.bldr.get_screen("seat_selection2").ids.seat79.disabled = True
                                elif self.bldr.get_screen("seat_selection2").ids.seat80.name == seat_no:
                                    self.bldr.get_screen("seat_selection2").ids.seat80.disabled = True
                                elif self.bldr.get_screen("seat_selection2").ids.seat81.name == seat_no:
                                    self.bldr.get_screen("seat_selection2").ids.seat81.disabled = True
                                elif self.bldr.get_screen("seat_selection2").ids.seat82.name == seat_no:
                                    self.bldr.get_screen("seat_selection2").ids.seat82.disabled = True
                                elif self.bldr.get_screen("seat_selection2").ids.seat83.name == seat_no:
                                    self.bldr.get_screen("seat_selection2").ids.seat83.disabled = True
                                elif self.bldr.get_screen("seat_selection2").ids.seat84.name == seat_no:
                                    self.bldr.get_screen("seat_selection2").ids.seat84.disabled = True
                            else:
                                self.enable_seat2(seat_no)


        except Exception as e:
            error_details = traceback.format_exc()
            self.show_error_dialog(f"Error: {e}\nDetails:\n{error_details}")

    def check_seat_availability1(self, other):
        if self.bldr.get_screen("seat_selection1").ids.seat1.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat1.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat2.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat2.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat3.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat3.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat4.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat4.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat5.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat5.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat6.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat6.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat7.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat7.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat8.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat8.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat9.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat9.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat10.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat10.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat11.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat11.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat12.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat12.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat13.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat13.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat14.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat14.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat15.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat15.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat16.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat16.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat17.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat17.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat18.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat18.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat19.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat19.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat20.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat20.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat21.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat21.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat22.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat22.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat23.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat23.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat24.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat24.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat25.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat25.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat26.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat26.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat27.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat27.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat28.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat28.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat29.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat29.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat30.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat30.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat31.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat31.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat32.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat32.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat33.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat33.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat34.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat34.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat35.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat35.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat36.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat36.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat37.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat37.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat38.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat38.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat39.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat39.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat40.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat40.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat41.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat41.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat42.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat42.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat43.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat43.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat44.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat44.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat45.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat45.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat46.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat46.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat47.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat47.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat48.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat48.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat49.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat49.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat50.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat50.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat51.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat51.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat52.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat52.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat53.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat53.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat54.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat54.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat55.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat55.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat56.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat56.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat57.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat57.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat58.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat58.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat59.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat59.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat60.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat60.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat61.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat61.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat62.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat62.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat63.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat63.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat64.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat64.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat65.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat65.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat66.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat66.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat67.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat67.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat68.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat68.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat69.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat69.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat70.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat70.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat71.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat71.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat72.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat72.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat73.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat73.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat74.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat74.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat75.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat75.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat76.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat76.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat77.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat77.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat78.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat78.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat79.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat79.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat80.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat80.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat81.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat81.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat82.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat82.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat83.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat83.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details1(other)
        elif self.bldr.get_screen("seat_selection1").ids.seat84.name == other:
            if self.bldr.get_screen("seat_selection1").ids.seat84.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details1(other)
        else:
            self.show_error_dialog("Please Select the Seat To Book!")

    def check_seat_availability2(self,other):
        if self.bldr.get_screen("seat_selection2").ids.seat1.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat1.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat2.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat2.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat3.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat3.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat4.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat4.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat5.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat5.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat6.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat6.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat7.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat7.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat8.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat8.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat9.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat9.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat10.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat10.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat11.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat11.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat12.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat12.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat13.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat13.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat14.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat14.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat15.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat15.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat16.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat16.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat17.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat17.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat18.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat18.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat19.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat19.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat20.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat20.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat21.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat21.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat22.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat22.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat23.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat23.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat24.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat24.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat25.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat25.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat26.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat26.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat27.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat27.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat28.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat28.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat29.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat29.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat30.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat30.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat31.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat31.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat32.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat32.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat33.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat33.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat34.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat34.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat35.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat35.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat36.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat36.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat37.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat37.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat38.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat38.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat39.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat39.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat40.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat40.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat41.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat41.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat42.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat42.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat43.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat43.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat44.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat44.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat45.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat45.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat46.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat46.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat47.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat47.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat48.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat48.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat49.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat49.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat50.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat50.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat51.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat51.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat52.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat52.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat53.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat53.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat54.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat54.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat55.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat55.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat56.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat56.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat57.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat57.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat58.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat58.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat59.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat59.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat60.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat60.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat61.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat61.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat62.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat62.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat63.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat63.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat64.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat64.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat65.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat65.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat66.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat66.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat67.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat67.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat68.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat68.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat69.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat69.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat70.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat70.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat71.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat71.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat72.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat72.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat73.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat73.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat74.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat74.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat75.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat75.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat76.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat76.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat77.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat77.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat78.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat78.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat79.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat79.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat80.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat80.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat81.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat81.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat82.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat82.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat83.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat83.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details2(other)
        elif self.bldr.get_screen("seat_selection2").ids.seat84.name == other:
            if self.bldr.get_screen("seat_selection2").ids.seat84.disabled == True:
                self.show_error_dialog("Please Select another Seat ,Seat is booked")
            else:
                self.get_on_time_details2(other)
        else:
            self.show_error_dialog("Please Select the Seat To Book!")

    def get_on_time_details1(self,other):
        self.username_after1 = MDTextField(
            hint_text="Username",
            icon_right="account",
            icon_right_color="#FFA500",
            text_color="Amber",
            size_hint=("50dp", "40dp"),
            height="30dp",
            font_size="25dp",
            line_color_normal="#FFFF00",
            line_color_focus="#FFA500",
            multiline=False,
            mode="rectangle",
            write_tab=False
        )
        self.dialog2 = MDDialog(
            title="Enter Username",
            type="custom",
            content_cls=self.username_after1,
            buttons=[
                MDRaisedButton(
                    text="Submit",
                    on_release=lambda _:self.booking_seat1(other)
                ),
                MDRaisedButton(
                    text="Cancel",
                    on_release=self.close_dialog1
                ),
            ],
        )
        self.dialog2.open()

    def get_on_time_details2(self,other):
        self.username_after2 = MDTextField(
            hint_text="Username",
            icon_right= "account",
            icon_right_color= "#FFA500",
            text_color="Amber",
            size_hint=("50dp", "40dp"),
            height="30dp",
            font_size= "25dp",
            line_color_normal= "#FFFF00",
            line_color_focus= "#FFA500",
            multiline= False,
            mode= "rectangle",
            write_tab= False
        )
        self.dialog3 = MDDialog(
            title="Enter Username",
            type="custom",
            content_cls=self.username_after2,
            buttons=[
                MDRaisedButton(
                    text="Submit",
                    on_release=lambda _:self.booking_seat2(other)
                ),
                MDRaisedButton(
                    text="Cancel",
                    on_release=self.close_dialog2
                ),
            ],
        )
        self.dialog3.open()

    def booking_seat1(self,other):
        seat_id1 = other
        self.dialog2.dismiss()
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
                                    update_data = json.dumps({"status": "Booked", "Booked_by": str(self.username_after1.text)})
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
                                            if seat_ids == seat_id1 and seat_status == "Booked" and seat_avail == str(self.username_after1.text):
                                                validated_seat = {
                                                    "seat_id": seat_ids,
                                                    "status": "Booked",
                                                    "Booked_by": str(self.username_after1.text)
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
                                                         to_time=str(self.to_selected_time), booked_by=str(self.username_after1.text))
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
                                            self.switch_to_user_dashboard()
                                        else:
                                            self.show_error_dialog("Unable to book seat!")
                                    except Exception as e:
                                        self.show_error_dialog(f"Error {e}")
                            except Exception as e:
                                self.show_error_dialog(f"Error {e}")
                        else:self.show_error_dialog("Please Select the Seat")
                    else:
                        path2 = "Past_booking"
                        url2 = f"{self.firebase_url}/{path2}.json"
                        if seat_name is not None:
                            past_booking_data = {
                                "seat_no": seat_name,
                                "date": str(self.formated_date),
                                "from_time": str(self.from_selected_time),
                                "to_time": str(self.to_selected_time),
                                "booked_by": str(self.username_after1.text)
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
                            self.show_error_dialog("Please Select the Seat")
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
                                "booked_by": str(self.username_after1.text)
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
                                            self.switch_to_user_dashboard()
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
                                "booked_by": str(self.username_after1.text)
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
                            "booked_by": str(self.username_after1.text)
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
                                        self.switch_to_user_dashboard()
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
                            "booked_by": str(self.username_after1.text)
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
        else:
            self.show_error_dialog("Please select a valid date in the future or today.")

    def booking_seat2(self,other):
        seat_id2 = other
        self.dialog3.dismiss()
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
                            if isinstance(seat_data,list):
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
                                if validated_seat and seat_id:
                                    update_url = f"{self.firebase_url}/{path}/{seat_id}.json"
                                    update_data = json.dumps({"status": "Booked", "Booked_by": str(self.username_after2.text)})
                                    update_response = requests.patch(update_url, data=update_data)
                                    if update_response.status_code == 200:
                                        self.show_error_dialog("Successfully, Seat Booked")
                                        self.switch_to_user_dashboard()
                                    else:
                                        self.show_error_dialog(
                                            f"Failed to Book Seat: {response.status_code}, {response.text}")
                    except Exception as e:
                        self.show_error_dialog(f"Error,{e}")
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
                                            if seat_ids == seat_id2 and seat_status == "Booked" and seat_avail == str(self.username_after2.text):
                                                validated_seat = {
                                                    "seat_id": seat_ids,
                                                    "status": "Booked",
                                                    "Booked_by": str(self.username_after2.text)
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
                                                         to_time=str(self.to_selected_time), booked_by=str(self.username_after2.text))
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
                                            self.switch_to_user_dashboard()
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
                        if seat_name is not None:
                            past_booking_data = {
                                "seat_no": seat_name,
                                "date": str(self.formated_date),
                                "from_time": str(self.from_selected_time),
                                "to_time": str(self.to_selected_time),
                                "booked_by": str(self.username_after2.text)
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
                            self.show_error_dialog("Please Select the Seat")

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
                                "booked_by": str(self.username_after2.text)
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
                                            self.switch_to_user_dashboard()
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
                                "booked_by": str(self.username_after2.text)
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
                            "booked_by": str(self.username_after2.text)
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
                                        self.switch_to_user_dashboard()
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
                            "booked_by": str(self.username_after2.text)
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
    def close_dialog1(self, instance=None):
        self.dialog2.dismiss()

    def close_dialog2(self,instance=None):
        self.dialog3.dismiss()

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

    def fetch_query_support(self):
        pass
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


if __name__ == '__main__':
    Window.size = (450, 600)
    AdminseatbookerApp().run()
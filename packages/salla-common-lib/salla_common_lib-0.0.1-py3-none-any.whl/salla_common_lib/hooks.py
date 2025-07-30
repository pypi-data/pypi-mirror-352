app_name = "salla_common_lib"
app_title = "Salla Common Lib"
app_publisher = "Golive-Solutions"
app_description = "App for salla common lib"
app_email = "info@golive-solutions.com"
app_license = "mit"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "salla_common_lib",
# 		"logo": "/assets/salla_common_lib/logo.png",
# 		"title": "Salla Common Lib",
# 		"route": "/salla_common_lib",
# 		"has_permission": "salla_common_lib.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/salla_common_lib/css/salla_common_lib.css"
# app_include_js = "/assets/salla_common_lib/js/salla_common_lib.js"

# include js, css files in header of web template
# web_include_css = "/assets/salla_common_lib/css/salla_common_lib.css"
# web_include_js = "/assets/salla_common_lib/js/salla_common_lib.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "salla_common_lib/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "salla_common_lib/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "salla_common_lib.utils.jinja_methods",
# 	"filters": "salla_common_lib.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "salla_common_lib.install.before_install"
# after_install = "salla_common_lib.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "salla_common_lib.uninstall.before_uninstall"
# after_uninstall = "salla_common_lib.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "salla_common_lib.utils.before_app_install"
# after_app_install = "salla_common_lib.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "salla_common_lib.utils.before_app_uninstall"
# after_app_uninstall = "salla_common_lib.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "salla_common_lib.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"salla_common_lib.tasks.all"
# 	],
# 	"daily": [
# 		"salla_common_lib.tasks.daily"
# 	],
# 	"hourly": [
# 		"salla_common_lib.tasks.hourly"
# 	],
# 	"weekly": [
# 		"salla_common_lib.tasks.weekly"
# 	],
# 	"monthly": [
# 		"salla_common_lib.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "salla_common_lib.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "salla_common_lib.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "salla_common_lib.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["salla_common_lib.utils.before_request"]
# after_request = ["salla_common_lib.utils.after_request"]

# Job Events
# ----------
# before_job = ["salla_common_lib.utils.before_job"]
# after_job = ["salla_common_lib.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"salla_common_lib.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }


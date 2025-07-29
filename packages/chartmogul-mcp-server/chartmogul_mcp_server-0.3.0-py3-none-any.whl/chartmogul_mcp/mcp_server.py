import sys
import datetime
from typing import Dict
from mcp.server.fastmcp import FastMCP
from chartmogul_mcp import api_client
from chartmogul_mcp import utils
from chartmogul_mcp.utils import LOGGER
from dotenv import load_dotenv


class ChartMogulMcp:

    def __init__(self):
        load_dotenv()

        # Initialize MCP Server
        self.mcp = FastMCP(utils.MCP_SERVER_NAME, deps=utils.DEPENDENCIES)
        LOGGER.info("ChartMogul MCP Server initialized")

        self.config = api_client.init_chartmogul_config()

        # Register MCP tools
        self._register_tools()


    def _register_tools(self):
        """Register MCP tools to interact with ChartMogul API."""

        ## account
        @self.mcp.tool(name='retrieve_account',
                       description='Retrieve some useful information about your ChartMogul account.')
        async def retrieve_account() -> Dict:
            return api_client.retrieve_account(self.config)

        ## data sources
        @self.mcp.tool(name='list_sources',
                       description='Get a list of all data sources in your ChartMogul account.'
                                   'You can also filter using the data source name or system '
                                   '(the type of system of the data sources, e.g., Stripe, Recurly, Custom, etc.).')
        async def list_sources(name: str = None, system: str = None) -> list:
            return api_client.list_sources(self.config, name, system)

        @self.mcp.tool(name='retrieve_source',
                       description='Retrieve a data source from your ChartMogul account using its UUID.')
        async def retrieve_source(uuid: str) -> Dict:
            return api_client.retrieve_source(self.config, uuid)

        ## customers
        @self.mcp.tool(name='list_customers',
                       description='Get a list of customers in your ChartMogul account. '
                                   'We have a default limit of 20 customers, '
                                   'ask but discourage the user if they want more than 20 as this will exhaust AI tokens.'
                                   'You can also filter based on data_source_uuid, external_id, '
                                   'status (one of New_Lead, Working_Lead, Qualified_Lead, Unqualified_Lead, Active, '
                                   'Past_Due or Cancelled) and system (the type of system of the data sources, '
                                   'e.g. Stripe, Recurly, Custom, etc.).')
        async def list_customers(data_source_uuid: str = None, external_id: str = None, status: str = None,
                                 system: str = None, limit: int = 20) -> list:
            return api_client.list_customers(self.config, data_source_uuid, external_id, status, system, limit)

        @self.mcp.tool(name='search_customers',
                       description='Search a list of all customers with the specified email address '
                                   'in your ChartMogul account.'
                                   'We have a default limit of 20 customers, '
                                   'ask but discourage the user if they want more than 20 as this will exhaust AI tokens.')
        async def search_customers(email: str, limit: int = 20) -> list:
            return api_client.search_customers(self.config, email, limit)

        @self.mcp.tool(name='retrieve_customer',
                       description='Retrieve a customer from your ChartMogul account using its UUID.')
        async def retrieve_customer(uuid: str) -> Dict:
            return api_client.retrieve_customer(self.config, uuid)

        @self.mcp.tool(name='create_customer',
                       description='Create a customer in your ChartMogul account. '
                                   'IMPORTANT: Always ask for ALL missing required details before creating a customer. '
                                   'Required fields are: data_source_uuid, external_id. '
                                   'Optional fields are: company, country (Country code of customer location as per '
                                   'ISO-3166 alpha-2 standard, e.g. US or DE), state (The US state where the customer '
                                   'is located — the US state code as per the ISO-3166-2 standard, e.g. US-CA or '
                                   'US-NY.), city, zip, lead_created_at (ISO 8601-formatted time, in the past), '
                                   'free_trial_started_at (ISO 8601-formatted time, in the past), '
                                   'attributes (an array containing the additional attributes of the customer '
                                   'in the form of tags and custom attributes; tags: An array of tags, '
                                   'custom: An array of custom attributes to be added to the customer. Each custom '
                                   'attribute must have a type, key and value), owner (email address of the user that '
                                   'owns this customer), primary_contact (object which contains first_name, last_name, '
                                   'email, title, phone, linked_in, twitter, notes), website_url.'
                                   'All fields should be included in a data dictionary.')
        async def create_customer(data: dict) -> Dict:
            return api_client.create_customer(self.config, data)

        @self.mcp.tool(name='update_customer',
                       description='Update certain modifiable attributes of a customer in your ChartMogul account. '
                                   'Attributes that can be modified are: company, lead_created_at, '
                                   'free_trial_started_at, zip, city, state, country, attributes '
                                   '(nested object which includes tags and custom object), owner, '
                                   'primary_contact, status and website_url, and should be included in a '
                                   'data dictionary.')
        async def update_customer(uuid: str, data: dict) -> Dict:
            return api_client.update_customer(self.config, uuid, data)

        @self.mcp.tool(name='list_customer_subscriptions',
                       description='Get a list of all subscriptions with the specified customer uuid '
                                   'in your ChartMogul account.'
                                   'We have a default limit of 20 subscriptions, '
                                   'ask but discourage the user if they want more than 20 as this will exhaust AI tokens.')
        async def list_customer_subscriptions(uuid: str, limit: int = 20) -> list:
            return api_client.list_customer_subscriptions(self.config, uuid, limit)

        @self.mcp.tool(name='list_customer_activities',
                       description='Get a list of all activities with the specified customer uuid '
                                   'in your ChartMogul account.'
                                   'We have a default limit of 20 activities, '
                                   'ask but discourage the user if they want more than 20 as this will exhaust AI tokens.')
        async def list_customer_activities(uuid: str, limit: int = 20) -> list:
            return api_client.list_customer_activities(self.config, uuid, limit)

        @self.mcp.tool(name='list_customer_attributes',
                       description='Get a list of all customer attributes with the specified customer uuid '
                                   'in your ChartMogul account.')
        async def list_customer_attributes(uuid: str) -> list:
            return api_client.list_customer_attributes(self.config, uuid)

        @self.mcp.tool(name='add_customer_tags',
                       description='Add a list of tags to the specified customer uuid in your ChartMogul account.'
                                   'This endpoint is idempotent, meaning that calling it multiple times with the same '
                                   'tags, no additional tags will be added to the customer. If the endpoint is '
                                   'called with a single new tag, it will be added to previous tags of the user.')
        async def add_customer_tags(uuid: str, tags: list) -> list:
            return api_client.add_customer_tags(self.config, uuid, tags)

        @self.mcp.tool(name='add_customer_custom_attributes',
                       description='Add a list of custom attributes to the specified customer uuid in your ChartMogul account.'
                                   'custom_attributes is an array containing the custom attributes to be added to the '
                                   'customer. Each custom attribute must have a type, key and value as described below:'
                                   'type: The data type of the custom attribute. Can be one of String, Integer, Decimal, '
                                   'Timestamp or Boolean. key: The name of the custom attribute. Accepts alphanumeric '
                                   'characters and underscores, value: The value of the custom attribute. '
                                   'Should be of the data type as specified in type. source: Optional parameter to '
                                   'specify where the custom attribute was created, displayed in the ChartMogul UI. '
                                   'Defaults to API.')
        async def add_customer_custom_attributes(uuid: str, custom_attributes: list) -> list:
            return api_client.add_customer_custom_attributes(self.config, uuid, custom_attributes)

        ## contacts
        @self.mcp.tool(name='list_contacts',
                       description='Get a list of all contacts in your ChartMogul account.'
                                   'We have a default limit of 20 contacts, '
                                   'ask but discourage the user if they want more than 20 as this will exhaust AI tokens.'
                                   'You can filter using the contact email address and the customer_external_id.')
        async def list_contacts(email: str = None, customer_external_id: str = None, limit: int = 20) -> list:
            return api_client.list_contacts(self.config, email, customer_external_id, limit)

        @self.mcp.tool(name='retrieve_contact',
                       description='Retrieve a contact from your ChartMogul account using its UUID.')
        async def retrieve_contact(uuid: str) -> Dict:
            return api_client.retrieve_contact(self.config, uuid)

        @self.mcp.tool(name='update_contact',
                       description='Update certain modifiable attributes of a contact in your ChartMogul account. '
                                   'Attributes that can be modified are: first_name, last_name, '
                                   'position, title, email, phone, linked_in, twitter, notes, custom '
                                   '(an array containing the custom attributes; each custom attribute must be defined '
                                   'as an object with a key and value), and should be included in a '
                                   'data dictionary.')
        async def update_contact(uuid: str, data: dict) -> Dict:
            return api_client.update_contact(self.config, uuid, data)

        @self.mcp.tool(name='create_contact',
                       description='Create a contact in your ChartMogul account. '
                                   'IMPORTANT: Always ask for ALL missing required details before creating a contact. '
                                   'Required fields are: customer_uuid, data_source_uuid. '
                                   'Optional fields are: first_name, last_name, position, title, email, phone, linked_in, '
                                   'twitter, notes, custom (an array containing the custom attributes; each '
                                   'custom attribute must be defined as an object with a key and value). '
                                   'All fields should be included in a data dictionary.')
        async def create_contact(data: dict) -> Dict:
            return api_client.create_contact(self.config, data)


        ## customer_notes
        @self.mcp.tool(name='list_customer_notes',
                       description='Get a list of all customer notes in your ChartMogul account.'
                                   'We have a default limit of 20 customer notes, '
                                   'ask but discourage the user if they want more than 20 as this will exhaust AI tokens.'
                                   'You can filter using the customer_uuid and the type (note or call).')
        async def list_customer_notes(customer_uuid: str = None, type: str = None, limit: int = 20) -> list:
            return api_client.list_customer_notes(self.config, customer_uuid, type, limit)

        @self.mcp.tool(name='retrieve_customer_note',
                       description='Retrieve a customer note from your ChartMogul account using its UUID.')
        async def retrieve_customer_note(uuid: str) -> Dict:
            return api_client.retrieve_customer_note(self.config, uuid)

        @self.mcp.tool(name='update_customer_note',
                       description='Update certain modifiable attributes of a customer note in your ChartMogul account. '
                                   'Attributes that can be modified are: author_email, text, '
                                   'call_duration (integer; relevant for type call; duration of the call in seconds), '
                                   'created_at (an ISO 8601-formatted time in the past), '
                                   'updated_at (an ISO 8601-formatted time in the past), and should be included in a '
                                   'data dictionary.')
        async def update_customer_note(uuid: str, data: dict) -> Dict:
            return api_client.update_customer_note(self.config, uuid, data)

        @self.mcp.tool(name='create_customer_note',
                       description='Create a customer note in your ChartMogul account. '
                                   'IMPORTANT: Always ask for ALL missing required details before creating a customer note. '
                                   'Required fields are: customer_uuid, type (call or note). '
                                   'Optional fields are: author_email, text, '
                                   'call_duration (integer; relevant for type call; duration of the call in seconds), '
                                   'created_at (an ISO 8601-formatted time in the past). '
                                   'All fields should be included in a data dictionary.')
        async def create_customer_note(data: dict) -> Dict:
            return api_client.create_customer_note(self.config, data)


        ## opportunities
        @self.mcp.tool(name='list_opportunities',
                       description='Get a list of all opportunities in your ChartMogul account.'
                                   'We have a default limit of 20 opportunities, '
                                   'ask but discourage the user if they want more than 20 as this will exhaust AI tokens.'
                                   'You can filter using the customer_uuid, owner (email address of the ChartMogul user '
                                   'with a CRM seat who is the primary salesperson responsible for this opportunity), '
                                   'pipeline, pipeline_stage, estimated_close_date_on_or_after '
                                   '(lower limit of the estimated close date range; an ISO 8601-formatted date) and '
                                   'estimated_close_date_on_or_before (upper limit of the estimated close date range; '
                                   'an ISO 8601-formatted date).')
        async def list_opportunities(customer_uuid: str = None, owner: str = None, pipeline: str = None,
                                     pipeline_stage: str = None,
                                     estimated_close_date_on_or_after: datetime.datetime =None,
                                     estimated_close_date_on_or_before: datetime.datetime =None,
                                     limit: int = 20) -> list:
            return api_client.list_opportunities(self.config, customer_uuid, owner, pipeline, pipeline_stage,
                                                 estimated_close_date_on_or_after, estimated_close_date_on_or_before,
                                                 limit)

        @self.mcp.tool(name='retrieve_opportunity',
                       description='Retrieve an opportunity from your ChartMogul account using its UUID.')
        async def retrieve_opportunity(uuid: str) -> Dict:
            return api_client.retrieve_opportunity(self.config, uuid)

        @self.mcp.tool(name='update_opportunity',
                       description='Update certain modifiable attributes of an opportunity in your ChartMogul account. '
                                   'Attributes that can be modified are: owner, pipeline, pipeline_stage, '
                                   'estimated_close_date, amount_in_cents, currency (The 3-letter currency code for '
                                   'the expected close value, e.g. USD, EUR or GBP), type (recurring or one-time), '
                                   'forecast_category (pipeline, best_case, committed, lost or won), win_likelihood '
                                   '(0-100), custom (list of custom attributes as key and value pairs) '
                                   'and should be included in a data dictionary.')
        async def update_opportunity(uuid: str, data: dict) -> Dict:
            return api_client.update_opportunity(self.config, uuid, data)

        @self.mcp.tool(name='create_opportunity',
                       description='Create an opportunity in your ChartMogul account. '
                                   'IMPORTANT: Always ask for ALL missing required details before creating an opportunity. '
                                   'Required fields are: customer_uuid, owner '
                                   '(email address of the ChartMogul user with a CRM seat who is the primary '
                                   'salesperson responsible for this opportunity), pipeline, '
                                   'pipeline_stage, estimated_close_date (an ISO 8601-formatted date), '
                                   'amount_in_cents, currency (The 3-letter currency code for the expected close value, '
                                   'e.g. USD, EUR or GBP). '
                                   'Optional fields: type (recurring or one-time), forecast_category (pipeline, '
                                   'best_case, committed, lost or won), win_likelihood (integer; 0-100), '
                                   'custom (list of custom attributes as key and value pairs). '
                                   'All fields should be included in a data dictionary.')
        async def create_opportunity(data: dict) -> Dict:
            return api_client.create_opportunity(self.config, data)


        ## plans
        @self.mcp.tool(name='list_plans',
                       description='Get a list of all plans in your ChartMogul account.'
                                   'We have a default limit of 20 plans, '
                                   'ask but discourage the user if they want more than 20 as this will exhaust AI tokens.'
                                   'You can filter using the data_source_uuid, external_id, and system (the billing system '
                                   'that the plan belongs to, e.g., Stripe, Recurly, Custom).')
        async def list_plans(data_source_uuid: str = None, external_id: str = None, system: str = None,
                             limit: int = 20) -> list:
            return api_client.list_plans(self.config, data_source_uuid, external_id, system, limit)

        @self.mcp.tool(name='retrieve_plan',
                       description='Retrieve a plan from your ChartMogul account using its UUID.')
        async def retrieve_plan(uuid: str) -> Dict:
            return api_client.retrieve_plan(self.config, uuid)

        @self.mcp.tool(name='update_plan',
                       description='Update certain modifiable attributes of a plan in your ChartMogul account. '
                                   'Attributes that can be modified are: name, interval_count '
                                   '(frequency of billing interval; accepts integers greater than 0, '
                                   'e.g., 6 for a half-yearly plan), interval_unit (day, month or year) '
                                   'and should be included in a data dictionary.')
        async def update_plan(uuid: str, data: dict) -> Dict:
            return api_client.update_plan(self.config, uuid, data)

        @self.mcp.tool(name='create_plan',
                       description='Create a plan in your ChartMogul account. '
                                   'IMPORTANT: Always ask for ALL missing required details before creating a plan. '
                                   'Required fields are: data_source_uuid, name, '
                                   'interval_count (frequency of billing interval; accepts integers greater than 0, '
                                   'e.g., 6 for a half-yearly plan), interval_unit (day, month or year). '
                                   'Optional field: external_id. '
                                   'All fields should be included in a data dictionary.')
        async def create_plan(data: dict) -> Dict:
            return api_client.create_plan(self.config, data)


        ## plan groups
        @self.mcp.tool(name='list_plan_groups',
                       description='Get a list of all plan groups in your ChartMogul account.'
                                   'We have a default limit of 20 plan groups, '
                                   'ask but discourage the user if they want more than 20 as this will exhaust AI tokens.')
        async def list_plan_groups(limit: int = 20) -> list:
            return api_client.list_plan_groups(self.config, limit)

        ## plan groups
        @self.mcp.tool(name='list_plan_group_plans',
                       description='Get a list of all plans in a plan group using its UUID.')
        async def list_plan_group_plans(uuid: str = None, limit: int = 20) -> list:
            return api_client.list_plan_group_plans(self.config, uuid, limit)

        @self.mcp.tool(name='retrieve_plan_group',
                       description='Retrieve a plan group from your ChartMogul account using its UUID.')
        async def retrieve_plan_group(uuid: str) -> Dict:
            return api_client.retrieve_plan_group(self.config, uuid)

        @self.mcp.tool(name='update_plan_group',
                       description='Update certain modifiable attributes of a plan group in your ChartMogul account. '
                                   'Attributes that can be modified are: name, plans '
                                   '(array of the uuids of the plans to be added to the plan group) '
                                   'and should be included in a data dictionary.')
        async def update_plan_group(uuid: str, data: dict) -> Dict:
            return api_client.update_plan_group(self.config, uuid, data)

        @self.mcp.tool(name='create_plan_group',
                       description='Create a plan group in your ChartMogul account. '
                                   'IMPORTANT: Always ask for ALL missing required details before creating a plan group. '
                                   'Required fields are: name, plans '
                                   '(array of the uuids of the plans to be added to the plan group) '
                                   'and should be included in a data dictionary.')
        async def create_plan_group(data: dict) -> Dict:
            return api_client.create_plan_group(self.config, data)


        ## tasks
        @self.mcp.tool(name='list_tasks',
                       description='Get a list of all tasks in your ChartMogul account.'
                                   'We have a default limit of 20 tasks, '
                                   'ask but discourage the user if they want more than 20 as this will exhaust AI tokens.'
                                   'You can filter using the customer_uuid, assignee (email address of the ChartMogul user '
                                   'with a CRM seat assigned to the task), due_date_on_or_after '
                                   '(lower limit of the due date range; an ISO 8601-formatted date), '
                                   'estimated_close_date_on_or_before (upper limit of the due date range; '
                                   'an ISO 8601-formatted date), completed (true or false).'
                       )
        async def list_tasks(customer_uuid: str = None, assignee: str = None,
                             due_date_on_or_after: datetime.datetime = None,
                             estimated_close_date_on_or_before: datetime.datetime = None, completed: bool = None,
                             limit: int = 20) -> list:
            return api_client.list_tasks(self.config, customer_uuid, assignee, due_date_on_or_after,
                                         estimated_close_date_on_or_before, completed, limit)

        @self.mcp.tool(name='retrieve_task',
                       description='Retrieve a task from your ChartMogul account using its UUID.')
        async def retrieve_task(uuid: str) -> Dict:
            return api_client.retrieve_task(self.config, uuid)

        @self.mcp.tool(name='update_task',
                       description='Update certain modifiable attributes of a task in your ChartMogul account. '
                                   'Attributes that can be modified are: task_details '
                                   '(up to 255 characters), assignee  (email address of the ChartMogul user '
                                   'with a CRM seat assigned to the task), due_date (an ISO 8601-formatted date), '
                                   'completed_at (an ISO 8601-formatted date) '
                                   'and should be included in a data dictionary.')
        async def update_task(uuid: str, data: dict) -> Dict:
            return api_client.update_task(self.config, uuid, data)

        @self.mcp.tool(name='create_task',
                       description='Create a task in your ChartMogul account. '
                                   'IMPORTANT: Always ask for ALL missing required details before creating a task. '
                                   'Required fields are: customer_uuid, task_details '
                                   '(up to 255 characters), assignee (email address of the ChartMogul user '
                                   'with a CRM seat assigned to the task), due_date (an ISO 8601-formatted date). '
                                   'Optional field: completed_at (an ISO 8601-formatted date).'
                                   'All fields should be included in a data dictionary.')
        async def create_task(data: dict) -> Dict:
            return api_client.create_task(self.config, data)

        ## metrics api
        @self.mcp.tool(name='all_metrics',
                       description='Retrieve all key metrics, for the specified time period, interval and filters. '
                                   'Metrics include: MRR, ARR, ARPA, ASP, customer count, customer churn rate, '
                                   'MRR churn rate and LTV. '
                                   'Provide the start-date, end-date and interval (possible values are day, week, month,'
                                   'quarter or year. Additional filter values include geo (A comma-separated list of ISO '
                                   '3166-1 Alpha-2 formatted country codes) and plans (A comma-separated list of '
                                   'plan names (as configured in your ChartMogul account), UUIDs and external IDs to '
                                   'filter the results. Spaces in plan names must be URL-encoded, '
                                   'e.g., Silver%20plan,Gold%20plan,Enterprise%20plan).'
                                   'All amounts are given in the selected currency of your account '
                                   'and are an integer number of cents. Divide by 100 to obtain the actual value.')
        async def all_metrics(start_date: str, end_date: str, interval: str, geo: str = None,
                              plans: str = None) -> list:
            return api_client.all_metrics(self.config, start_date, end_date, interval, geo, plans)

        @self.mcp.tool(name='mrr_metrics',
                       description='Retrieve Monthly Recurring Revenue (MRR) metrics, for the specified time period, interval and filters. '
                                   'Provide the start-date, end-date and interval (possible values are day, week, month,'
                                   'quarter or year. Additional filter values include geo (A comma-separated list of ISO '
                                   '3166-1 Alpha-2 formatted country codes) and plans (A comma-separated list of '
                                   'plan names (as configured in your ChartMogul account), UUIDs and external IDs to '
                                   'filter the results. Spaces in plan names must be URL-encoded, '
                                   'e.g., Silver%20plan,Gold%20plan,Enterprise%20plan).'
                                   'All amounts are given in the selected currency of your account '
                                   'and are an integer number of cents. Divide by 100 to obtain the actual value.')
        async def mrr_metrics(start_date: str, end_date: str, interval: str, geo: str = None,
                              plans: str = None) -> list:
            return api_client.mrr_metrics(self.config, start_date, end_date, interval, geo, plans)

        @self.mcp.tool(name='arr_metrics',
                       description='Retrieve Annualized Run Rate (ARR) metrics, for the specified time period, interval and filters. '
                                   'Provide the start-date, end-date and interval (possible values are day, week, month,'
                                   'quarter or year. Additional filter values include geo (A comma-separated list of ISO '
                                   '3166-1 Alpha-2 formatted country codes) and plans (A comma-separated list of '
                                   'plan names (as configured in your ChartMogul account), UUIDs and external IDs to '
                                   'filter the results. Spaces in plan names must be URL-encoded, '
                                   'e.g., Silver%20plan,Gold%20plan,Enterprise%20plan).'
                                   'All amounts are given in the selected currency of your account '
                                   'and are an integer number of cents. Divide by 100 to obtain the actual value.')
        async def arr_metrics(start_date: str, end_date: str, interval: str, geo: str = None,
                              plans: str = None) -> list:
            return api_client.arr_metrics(self.config, start_date, end_date, interval, geo, plans)

        @self.mcp.tool(name='arpa_metrics',
                       description='Retrieve Average Revenue Per Account (ARPA) metrics, for the specified time period, interval and filters. '
                                   'Provide the start-date, end-date and interval (possible values are day, week, month,'
                                   'quarter or year. Additional filter values include geo (A comma-separated list of ISO '
                                   '3166-1 Alpha-2 formatted country codes) and plans (A comma-separated list of '
                                   'plan names (as configured in your ChartMogul account), UUIDs and external IDs to '
                                   'filter the results. Spaces in plan names must be URL-encoded, '
                                   'e.g., Silver%20plan,Gold%20plan,Enterprise%20plan).'
                                   'All amounts are given in the selected currency of your account '
                                   'and are an integer number of cents. Divide by 100 to obtain the actual value.')
        async def arpa_metrics(start_date: str, end_date: str, interval: str, geo: str = None,
                               plans: str = None) -> list:
            return api_client.arpa_metrics(self.config, start_date, end_date, interval, geo, plans)

        @self.mcp.tool(name='asp_metrics',
                       description='Retrieve Average Sale Price (ASP) metrics, for the specified time period, interval and filters. '
                                   'Provide the start-date, end-date and interval (possible values are month,'
                                   'quarter or year. Additional filter values include geo (A comma-separated list of ISO '
                                   '3166-1 Alpha-2 formatted country codes) and plans (A comma-separated list of '
                                   'plan names (as configured in your ChartMogul account), UUIDs and external IDs to '
                                   'filter the results. Spaces in plan names must be URL-encoded, '
                                   'e.g., Silver%20plan,Gold%20plan,Enterprise%20plan).'
                                   'All amounts are given in the selected currency of your account '
                                   'and are an integer number of cents. Divide by 100 to obtain the actual value.')
        async def asp_metrics(start_date: str, end_date: str, interval: str, geo: str = None,
                              plans: str = None) -> list:
            return api_client.asp_metrics(self.config, start_date, end_date, interval, geo, plans)

        @self.mcp.tool(name='customer_count_metrics',
                       description='Retrieve customer count metrics, for the specified time period, interval and filters. '
                                   'Provide the start-date, end-date and interval (possible values are day, week, month,'
                                   'quarter or year. Additional filter values include geo (A comma-separated list of ISO '
                                   '3166-1 Alpha-2 formatted country codes) and plans (A comma-separated list of '
                                   'plan names (as configured in your ChartMogul account), UUIDs and external IDs to '
                                   'filter the results. Spaces in plan names must be URL-encoded, '
                                   'e.g., Silver%20plan,Gold%20plan,Enterprise%20plan).')
        async def customer_count_metrics(start_date: str, end_date: str, interval: str, geo: str = None,
                                         plans: str = None) -> list:
            return api_client.customer_count_metrics(self.config, start_date, end_date, interval, geo, plans)

        @self.mcp.tool(name='customer_churn_rate_metrics',
                       description='Retrieve customer churn rate metrics, for the specified time period, interval and filters. '
                                   'Provide the start-date, end-date and interval (possible values are day, week, month,'
                                   'quarter or year. Additional filter values include geo (A comma-separated list of ISO '
                                   '3166-1 Alpha-2 formatted country codes) and plans (A comma-separated list of '
                                   'plan names (as configured in your ChartMogul account), UUIDs and external IDs to '
                                   'filter the results. Spaces in plan names must be URL-encoded, '
                                   'e.g., Silver%20plan,Gold%20plan,Enterprise%20plan).')
        async def customer_churn_rate_metrics(start_date: str, end_date: str, interval: str, geo: str = None,
                                              plans: str = None) -> list:
            return api_client.customer_churn_rate_metrics(self.config, start_date, end_date, interval, geo, plans)

        @self.mcp.tool(name='mrr_churn_rate_metrics',
                       description='Retrieve Net MRR Churn Rate metrics, for the specified time period, interval and filters. '
                                   'Provide the start-date, end-date and interval (possible values are day, week, month,'
                                   'quarter or year. Additional filter values include geo (A comma-separated list of ISO '
                                   '3166-1 Alpha-2 formatted country codes) and plans (A comma-separated list of '
                                   'plan names (as configured in your ChartMogul account), UUIDs and external IDs to '
                                   'filter the results. Spaces in plan names must be URL-encoded, '
                                   'e.g., Silver%20plan,Gold%20plan,Enterprise%20plan).')
        async def mrr_churn_rate_metrics(start_date: str, end_date: str, interval: str, geo: str = None,
                                         plans: str = None) -> list:
            return api_client.mrr_churn_rate_metrics(self.config, start_date, end_date, interval, geo, plans)

        @self.mcp.tool(name='ltv_metrics',
                       description='Retrieve Customer Lifetime Value (LTV) metrics, for the specified time period, and filters. '
                                   'Provide the start-date, end-date. Additional filter values include geo (A comma-separated list of ISO '
                                   '3166-1 Alpha-2 formatted country codes) and plans (A comma-separated list of '
                                   'plan names (as configured in your ChartMogul account), UUIDs and external IDs to '
                                   'filter the results. Spaces in plan names must be URL-encoded, '
                                   'e.g., Silver%20plan,Gold%20plan,Enterprise%20plan).'
                                   'All amounts are given in the selected currency of your account '
                                   'and are an integer number of cents. Divide by 100 to obtain the actual value.')
        async def ltv_metrics(start_date: str, end_date: str, interval: str, geo: str = None,
                              plans: str = None) -> list:
            return api_client.ltv_metrics(self.config, start_date, end_date, interval, geo, plans)

        ## subscription events
        @self.mcp.tool(name='list_subscription_events',
                       description='Get a list of all subscription events in your ChartMogul account.'
                                   'We have a default limit of 20 subscription events, '
                                   'ask but discourage the user if they want more than 20 as this will exhaust AI tokens.'
                                   'You can filter using the data_source_uuid, external_id of a subscription event, '
                                   'customer_external_id, subscription_external_id, event_type (one of '
                                   'subscription_start, subscription_start_scheduled, '
                                   'scheduled_subscription_start_retracted, subscription_cancelled, '
                                   'subscription_cancellation_scheduled, scheduled_subscription_cancellation_retracted, '
                                   'subscription_updated, subscription_update_scheduled, '
                                   'scheduled_subscription_update_retracted, subscription_event_retracted), event_date '
                                   '(an ISO 8601 formatted time), effective_date (an ISO 8601 formatted time), '
                                   'plan_external_id.')
        async def list_subscription_events(data_source_uuid: str = None, external_id: str = None, customer_external_id: str = None,
                                           subscription_external_id: str = None, event_type: str = None,
                                           event_date: datetime.datetime = None,
                                           effective_date: datetime.datetime = None, plan_external_id: str = None,
                                           limit: int = 20) -> list:
            return api_client.list_subscription_events(self.config, data_source_uuid, external_id, customer_external_id,
                                                       subscription_external_id, event_type, event_date, effective_date,
                                                       plan_external_id, limit)

        ## invoices
        @self.mcp.tool(name='list_invoices',
                       description='Get a list of all invoices in your ChartMogul account.'
                                   'We have a default limit of 20 invoices, '
                                   'ask but discourage the user if they want more than 20 as this will exhaust AI tokens.'
                                   'You can filter using the data_source_uuid, invoice external_id, customer_uuid and '
                                   'validation_type (one of valid, invalid or all).')
        async def list_invoices(data_source_uuid: str = None, external_id: str = None, customer_uuid: str = None,
                                validation_type: str = None, limit: int = 20) -> list:
            return api_client.list_invoices(self.config, data_source_uuid, external_id, customer_uuid, validation_type,
                                            limit)

        ## activities
        @self.mcp.tool(name='list_activities',
                       description='Get a list of all activities in your ChartMogul account.'
                                   'We have a default limit of 20 activities, '
                                   'ask but discourage the user if they want more than 20 as this will exhaust AI tokens.'
                                   'You can filter with start_date (an ISO 8601 formatted time), end_date '
                                   '(an ISO 8601 formatted time), type (one of new_biz, reactivation, expansion, '
                                   'contraction or churn) and order (Setting value as -date returns results in '
                                   'descending order with the latest activity returned first, while date returns '
                                   'results in ascending order.). ')
        async def list_activities(start_date: datetime.datetime = None, end_date: datetime.datetime = None,
                                  type: str = None, order: str = None, limit: int = 20) -> list:
            return api_client.list_activities(self.config, start_date, end_date, type, order, limit)


    def run(self):
        """Start the MCP server."""
        try:
            LOGGER.info("Running MCP Server for ChartMogul API interactions")
            self.mcp.run(transport="stdio")
        except Exception as e:
            LOGGER.error(f"Fatal Error in ChartMogul MCP Server: {str(e)}", exc_info=True)
            sys.exit(1)

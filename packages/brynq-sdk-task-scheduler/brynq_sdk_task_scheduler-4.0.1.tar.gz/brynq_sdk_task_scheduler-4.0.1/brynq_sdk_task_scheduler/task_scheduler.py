import sys
import os
import datetime
import inspect
import time
from typing import Literal, List, Optional
import traceback
import pandas as pd
import json
import pymysql
import requests
from brynq_sdk_mandrill import MailClient
from brynq_sdk_functions import Functions
from brynq_sdk_mysql import MySQL
from brynq_sdk_elastic import Elastic
from brynq_sdk_brynq import BrynQ
import warnings
import re


class TaskScheduler:

    def __init__(self, data_interface_id: int = None, loglevel: str = 'INFO', email_after_errors: bool = False):
        """
        The TaskScheduler is responsible for the logging to the database. Based on this logging, the next reload will
        start or not and warning will be given or not
        :param data_interface_id: The ID from the task as saved in the task_scheduler table in the customer database
        :param email_after_errors: a True or False value. When True, there will be send an email to a contactperson of the customer (as given in the database) with the number of errors
        :param loglevel: Chose on which level you want to store the logs. Default is INFO. that means that a logline
        :param disable_logging: If the interface is started from a local instance, logs will not be stored by default. If this is set to True, the logs will be stored in the database
        with level DEBUG not is stored
        """
        # If the task is started via the task_scheduler, the following parameters will be passed by the scheduler.
        # The distinction between local and non local is made because the scheduler usually sets the scheduler_log table entry and run_id. When running locally, the tasks will not log anything by default.
        if any(flag in sys.argv[0].split('/') for flag in ['opt', 'home']):
            self.started_local = True
            self.run_id = int(round(time.time() * 100000))
            self.task_id = None
            self.data_interface_id = data_interface_id
            # set it into environment variables for reuse in source and target systems
            os.environ['DATA_INTERFACE_ID'] = str(self.data_interface_id)
            self.mysql_enabled = False
            self.elastic_enabled = False
            print("You're running locally, so your task won't be started in the platform and logs won't be saved")
        else:
            self.started_local = False
            self.customer_db, self.task_id, self.run_id, self.data_interface_id = sys.argv[1:5]
            self.mysql_enabled = True
            self.elastic_enabled = True
        # If the task is started locally, the parameters should be set locally

        print(f"Run ID: {self.run_id}, Data Interface ID: {self.data_interface_id}, Task ID: {self.task_id}, Started Locally: {self.started_local}")
        self.brynq = BrynQ()
        self.email_after_errors = email_after_errors
        # Set up local log directory
        self.local_log_dir = 'local_logs'
        os.makedirs(self.local_log_dir, exist_ok=True)

        try:
            self.customer_db = os.getenv("MYSQL_DATABASE")
            self.customer = os.getenv('BRYNQ_SUBDOMAIN').lower().replace(' ', '_')
            self.partner_id = os.getenv('PARTNER_ID').lower().replace(' ', '_') if os.getenv('PARTNER_ID') else 'brynq'
            self.loglevel = loglevel
            self.started_at = datetime.datetime.now()
            self.error_count = 0

            # Check if the log tables exists in the customer database1. If not, create them
            # Mysql throws a warning when a table already exists. We don't care so we ignore warnings. (not exceptions!)
            warnings.filterwarnings('ignore')

            # Initialize MySQL
            self.mysql_reachable = True
            try:
                self.mysql = MySQL()
                self.mysql.ping()
            except Exception as e:
                self.mysql_reachable = False
                self.mysql = None
                print("MySQL is not reachable, logs will be saved locally if needed.")

            # Start the task and setup the data in the database
            if self.mysql_enabled and self.mysql_reachable:
                self.customer_id = self.mysql.raw_query(f'SELECT id FROM sc.customers WHERE dbname = \'{self.customer_db}\'')[0][0]
                self._process_local_mysql_logs()
                self._start_task()
        except Exception as e:
            self.error_handling(e)

    def __count_keys(self, json_obj):
        if not isinstance(json_obj, dict):
            return 0
        key_count = 0
        for key, value in json_obj.items():
            if not isinstance(value, dict):
                key_count += 1  # Count the current key
            else:
                key_count += self.__count_keys(value)  # Recursively count keys in nested dictionaries
        return key_count

    def __get_caller_info(self):
        stack = inspect.stack()
        caller_frame = stack[2][0]
        file_name = caller_frame.f_code.co_filename
        line_number = caller_frame.f_lineno
        function_name = stack[2][3]
        return file_name, line_number, function_name

    def create_task_execution_steps(self, step_details: list):
        """
        Check if the given steps already exists in the task_execution_steps table. If not, update or insert the values in the table
        :param step_details: list of dicts. Each dict must contain task details according to required_fields.
        Example: step_details = [
                                    {'nr': 1, 'description': 'test'},
                                    {'nr': 2, 'description': 'test2'}
                                ]
        :return: error (str) or response of mysql
        """
        warnings.warn("Execution steps are deprecated, please stop calling this method. It does nothing anymore", DeprecationWarning)

    def _start_task(self):
        """
        Start the task and write this to the database. While the status is running, the task will not start again
        :return: if the update to the database is successful or not
        """
        # If the task is started from a local instance (not the task_scheduler), create a start log row in the task_scheduler_log
        if self.started_local:
            self.mysql.raw_query(f"INSERT INTO `task_scheduler_log` (reload_id, task_id, reload_status, started_at, finished_at) VALUES ({self.run_id}, {self.task_id}, 'Running', '{self.started_at}', null)", insert=True)

        self.mysql.update('task_scheduler', ['status', 'step_nr'], ['RUNNING', 1], f'WHERE `id` = {self.task_id}')

    def db_variable(self, variable_name: str):
        """
        Get a value from the task_variables table corresponding with the given name. If temp value is filled, it will
        (run_instant = 1), then the temp_value will be returned. This is to give the possibility for users in the frontend to run
        a task once manual with other values then normal without overwriting the normal values.
        :param variable_name: the name of the variable
        :return: the value of the given variable.
        """
        warnings.deprecated("Use self.brynq.interfaces.get_variables() instead")

        variable = self.brynq.interfaces.get_variables(variable_name=variable_name)

        return variable

    def write_execution_log(self, message: str, data, loglevel: str = 'INFO', full_extract: bool = False):
        """
        Writes messages to the database. Give the message and the level of the log
        :param message: A string with a message for the log
        :param loglevel: You can choose between DEBUG, INFO, ERROR or CRITICAL (DEBUG is most granulated, CRITICAL the less)
        :param data: Uploaded data by the interface that has to be logged in ElasticSearch, if you have nothing to log, use None
        :param full_extract: If the data is a full load, set this to True. This will prevent the payload from being logged in ElasticSearch
        :return: If writing to the database is successful or not
        """
        # Validate if the provided loglevel is valid
        allowed_loglevels = ['DEBUG', 'INFO', 'ERROR', 'CRITICAL']
        if loglevel not in allowed_loglevels:
            raise ValueError(f"You\'ve entered a not allowed loglevel. Choose one of: {','.join(allowed_loglevels)}")

        # Get the linenumber from where the logline is executed.
        file_name, line_number, function_name = self.__get_caller_info()
        print('{} at line: {}'.format(message, line_number))

        # Count the errors for relevant log levels
        if loglevel == 'ERROR' or loglevel == 'CRITICAL':
            self.error_count += 1

        # Write the logline to the MYSQL database, depends on the chosen loglevel in the task
        if self.mysql_enabled:
            mysql_log_data = {
                'reload_id': self.run_id,
                'task_id': self.task_id,
                'log_level': loglevel,
                'created_at': datetime.datetime.now(),
                'line_number': line_number,
                'message': re.sub("[']", '', message)
            }
            if self.mysql_reachable:
                try:
                    query = f"INSERT INTO `task_execution_log` (reload_id, task_id, log_level, created_at, line_number, message) VALUES ({mysql_log_data['reload_id']}, {mysql_log_data['task_id']}, '{mysql_log_data['log_level']}', '{mysql_log_data['created_at']}', {mysql_log_data['line_number']}, '{mysql_log_data['message']}')"
                    if self.loglevel == 'DEBUG' or (self.loglevel == 'INFO' and loglevel != 'DEBUG') or (self.loglevel == 'ERROR' and loglevel in ['ERROR', 'CRITICAL']) or (self.loglevel == 'CRITICAL' and loglevel == 'CRITICAL'):
                        self.mysql.raw_query(query, insert=True)
                except (pymysql.err.OperationalError, pymysql.err.InterfaceError) as e:
                    print(f"MySQL connection lost or closed during logging: {e}")
                    self.mysql_reachable = False
                    self._save_log_locally(mysql_log_data, 'mysql')
                except Exception as e:
                    print(f"Error during logging to MySQL: {e}")
                    self._save_log_locally(mysql_log_data, 'mysql')
            else:
                self._save_log_locally(mysql_log_data, 'mysql')

    def update_execution_step(self, step_number: int):
        """
        Update the current step number in the task_scheduler table so that user's in the frontend of BrynQ can see where a task is at any moment
        :param step_number: Give only a number
        :return: nothing
        """
        # Update the step number in the task_scheduler table
        warnings.warn("Execution steps are deprecated, please stop calling this method. It does nothing anymore", DeprecationWarning)

    def error_handling(self, e: Exception, breaking=True, send_to_teams=False):
        """
        This function handles errors that occur in the scheduler. Logs the traceback, updates run statuses and notifies users
        :param e: the Exception that is to be handled
        :param task_id: The scheduler task id
        :param mysql_con: The connection which is used to update the scheduler task status
        :param logger: The logger that is used to write the logging status to
        :param breaking: Determines if the error is breaking or code will continue
        :param started_at: Give the time the task is started
        :return: nothing
        """
        # Get the linenumber from where the logline is executed.
        file_name, line_number, function_name = self.__get_caller_info()

        # Format error to a somewhat readable format
        exc_type, exc_obj, exc_tb = sys.exc_info()
        error = str(e)[:400].replace('\'', '').replace('\"', '') + ' | Line: {}'.format(exc_tb.tb_lineno)

        if self.mysql_enabled:
            try:
                now = datetime.datetime.now()
                # Log to log table in the database
                mysql_log_data = {
                    'reload_id': self.run_id,
                    'task_id': self.task_id,
                    'log_level': 'CRITICAL',
                    'created_at': now,
                    'line_number': exc_tb.tb_lineno,
                    'message': error
                }
                self.error_count += 1
                # Get scheduler task details for logging
                task_details = \
                    self.mysql.select('task_scheduler, data_interfaces', 'data_interfaces.docker_image, data_interfaces.runfile_path', 'WHERE task_scheduler.data_interface_id = data_interfaces.id AND task_scheduler.id = {}'.format(self.task_id))[0]
                taskname = task_details[0]
                customer = task_details[1].split('/')[-1].split('.')[0]

                query = f"INSERT INTO `task_execution_log` (reload_id, task_id, log_level, created_at, line_number, message) VALUES ({mysql_log_data['reload_id']}, {mysql_log_data['task_id']}, '{mysql_log_data['log_level']}', '{mysql_log_data['created_at']}', {mysql_log_data['line_number']}, '{mysql_log_data['message']}')"
                self.mysql.raw_query(query, insert=True)

                if send_to_teams:
                    Functions.send_error_to_teams(database=customer, task_number=self.task_id, task_title=taskname)
                if breaking:
                    # Set scheduler status to failed
                    self.mysql.update('task_scheduler', ['status', 'last_reload', 'last_error_message', 'step_nr'],
                                      ['IDLE', now, 'Failed', 0],
                                      f'WHERE `id` = {self.task_id}')

                    self.mysql.update(table='task_scheduler_log',
                                      columns=['reload_status', 'finished_at'],
                                      values=['Failed', f'{now}'],
                                      filter=f'WHERE `reload_id` = {self.run_id}')
                    if self.email_after_errors:
                        self.email_errors(failed=True)
                    # Remove the temp values from the variables table
                    self.mysql.raw_query(f'UPDATE `task_variables` SET temp_value = null WHERE task_id = {self.task_id}', insert=True)

                    # Start the chained tasks if it there are tasks which should start if this one is failed
                    self.start_chained_tasks(finished_task_status='FAILED')
            except (pymysql.err.OperationalError, pymysql.err.InterfaceError) as e:
                print(f"MySQL connection lost or closed during logging: {e}")
                self.mysql_reachable = False
                self._save_log_locally(mysql_log_data, 'mysql')
            except Exception as e:
                print(f"Error during logging to MySQL: {e}")
                self._save_log_locally(mysql_log_data, 'mysql')

        # if breaking, reraise for clear traceback (local development) or just print if not breaking
        if breaking:
            raise e
        else:
            print(error)

    def finish_task(self, reload_instant=False, log_limit: Optional[int] = 10000, log_date_limit: datetime.date = None):
        """
        At the end of the script, write the outcome to the database. Write if the task is finished with or without errors, Email to a contactperson if this variable is given in the
        variables table. Also clean up the execution_log table when the number of lines is more than 1000
        :param reload_instant: If the task should start again after it's finished
        :param log_limit: The maximum number of logs to keep in the database. If the number of logs exceeds this limit, the oldest logs will be deleted.
        :param log_date_limit: The date from which logs should be kept. If this is set, logs older than this date will be deleted.
        :return:
        """
        if self.mysql_enabled:
            # If reload instant is true, this adds an extra field 'run_instant' to the update query, and sets the value to 1. This makes the task reload immediately after it's finished
            field = ['run_instant', 'next_reload'] if reload_instant else []
            value = ['1', datetime.datetime.now()] if reload_instant else []
            if self.error_count > 0:
                self.mysql.update('task_scheduler', ['status', 'last_reload', 'last_error_message', 'step_nr'],
                                  ['IDLE', datetime.datetime.now(), 'FinishedWithErrors', 0],
                                  'WHERE `id` = {}'.format(self.task_id))
                self.mysql.update(table='task_scheduler_log',
                                  columns=['reload_status', 'finished_at'],
                                  values=['FinishedWithErrors', f'{datetime.datetime.now()}'],
                                  filter=f'WHERE `reload_id` = {self.run_id}')
                # If the variable self.send_mail_after_errors is set to True, send an email with the number of errors to the given user
                if self.email_after_errors:
                    self.email_errors(failed=False)
            else:
                self.mysql.update(table='task_scheduler',
                                  columns=['status', 'last_reload', 'last_error_message', 'step_nr', 'stopped_by_user'] + field,
                                  values=['IDLE', datetime.datetime.now(), 'FinishedSucces', 0, 0] + value,
                                  filter='WHERE `id` = {}'.format(self.task_id))

                self.mysql.update(table='task_scheduler_log',
                                  columns=['reload_status', 'finished_at'],
                                  values=['FinishedSuccess', f'{datetime.datetime.now()}'],
                                  filter=f'WHERE `reload_id` = {self.run_id}')

            # Remove the temp values from the variables table
            self.mysql.raw_query(f'UPDATE `task_variables` SET temp_value = null WHERE task_id = {self.task_id}', insert=True)

            # Start the new task if it there is a task which should start if this one is finished
            self.start_chained_tasks(finished_task_status='SUCCESS')

            # Clean up execution log
            # set this date filter above the actual delete filter because of the many uncooperative quotation marks involved in the whole filter
            log_date_limit_filter = f"AND created_at >= \'{log_date_limit.strftime('%Y-%m-%d')}\'" if log_date_limit is not None else None
            delete_filter = f"WHERE task_id = {self.task_id} " \
                            f"AND reload_id NOT IN (SELECT reload_id FROM (SELECT reload_id FROM `task_execution_log` WHERE task_id = {self.task_id} " \
                            f"AND log_level != 'CRITICAL' " \
                            f"AND log_level != 'ERROR' " \
                            f"{log_date_limit_filter if log_date_limit_filter is not None else ''} " \
                            f"ORDER BY created_at DESC {f' LIMIT {log_limit} ' if log_limit is not None else ''}) temp)"
            resp = self.mysql.delete(table="task_execution_log", filter=delete_filter)
            print(resp)
        print(f'{datetime.datetime.now()} - Task finished')

    def start_chained_tasks(self, finished_task_status: str):
        if self.mysql_enabled:
            # only start chained tasks when trigger is on other task, otherwise this has changed in the db
            filter = f'WHERE start_after_task_id = \'{self.task_id}\' AND start_after_preceding_task = \'{finished_task_status}\' AND task_type = \'OTHER_TASK\''
            response = self.mysql.select(table='task_scheduler', selection='id', filter=filter)
            if len(response) > 0:
                tasks_to_run = [str(task[0]) for task in response]
                self.mysql.update(table='task_scheduler', columns=['run_instant'], values=['1'], filter=f'WHERE id IN({",".join(tasks_to_run)})')
        else:
            print("Unable to start chained tasks, MySQL is disabled")

    def email_errors(self, failed):
        # The mails to email to should be stored in the task_variables table with the variable email_errors_to
        email_variable = self.brynq.interfaces.get_variables(variable_name='email_errors_to')
        if email_variable is not None:
            email_to = email_variable.split(',')
            if isinstance(email_to, list):
                # The email_errors_to variable is a simple string. Convert it to a list and add a name because mandrill is asking for it
                email_list = []
                for i in email_to:
                    email_list.append({'name': 'BrynQ User', 'mail': i.strip()})

                # Recieve the task name and the finished_at time from the task_scheduler table joined with the data_interfaces table
                response = self.mysql.select(
                    table='task_scheduler LEFT JOIN data_interfaces ON task_scheduler.data_interface_id = data_interfaces.id ',
                    selection="title, last_reload",
                    filter=f'WHERE task_scheduler.id = {self.task_id}'
                )
                task = response[0][0]
                finished_at = response[0][1]

                # Set the content of the mail and all other stuff
                if failed:
                    subject = f'Task \'{task}\' has failed'
                    content = f'Task \'{task}\' with task ID \'{self.task_id}\' failed during its last run and was stopped at {finished_at}. ' \
                              f'The task is failed. ' \
                              f'to visit the BrynQ scheduler, click here: <a href="https://app.brynq.com/interfaces/">here</a>. Here you can find the logs and find more information on why this task had failed.'
                else:
                    subject = f'Task \'{task}\' is finished with errors'
                    content = f'Task \'{task}\' with ID \'{self.task_id}\' has runned and is finished at {finished_at}. ' \
                              f'The task is finished with {self.error_count} errors. ' \
                              f'to visit the BrynQ scheduler, click here: <a href="https://app.brynq.com/interfaces/">here</a>. Here you can find the logs and find more information on why this task had some errors.'
                MailClient().send_mail(email_to=email_list, subject=subject, content=content, language='EN')

    def _save_log_locally(self, payload, system):
        # system is 'mysql' or 'elastic'
        log_file_path = os.path.join(self.local_log_dir, f'{system}_log_{self.run_id}.json')
        try:
            if os.path.exists(log_file_path):
                with open(log_file_path, 'r') as f:
                    logs = json.load(f)
            else:
                logs = []
            logs.append(payload)
            with open(log_file_path, 'w') as f:
                json.dump(logs, f)
        except Exception as e:
            print(f"Error saving log locally: {e}")

    def _process_local_mysql_logs(self):
        mysql_log_files = [f for f in os.listdir(self.local_log_dir) if f.startswith('mysql_log_')]
        for log_file in mysql_log_files:
            log_file_path = os.path.join(self.local_log_dir, log_file)
            try:
                with open(log_file_path, 'r') as f:
                    logs = json.load(f)
                # Process logs
                for log_entry in logs:
                    self._write_log_to_mysql(log_entry)
                # Remove the log file after processing
                os.remove(log_file_path)
            except Exception as e:
                print(f"Error processing MySQL log file {log_file}: {e}")

    def _write_log_to_mysql(self, log_entry):
        """
        Insert a log entry dictionary into the task_execution_log table in MySQL.
        :param log_entry: dict with keys matching the columns of task_execution_log
        """
        try:
            query = (
                "INSERT INTO `task_execution_log` "
                "(reload_id, task_id, log_level, created_at, line_number, message) "
                "VALUES ({reload_id}, {task_id}, '{log_level}', '{created_at}', {line_number}, '{message}')"
            ).format(
                reload_id=log_entry['reload_id'],
                task_id=log_entry['task_id'],
                log_level=log_entry['log_level'],
                created_at=log_entry['created_at'],
                line_number=log_entry['line_number'],
                message=str(log_entry['message']).replace("'", "")
            )
            self.mysql.raw_query(query, insert=True)
        except Exception as e:
            print(f"Error writing log entry to MySQL: {e}")

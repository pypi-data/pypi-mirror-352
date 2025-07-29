import logging
import time
from argparse import ArgumentParser

import requests
import json
import datetime as dt
from abc import ABC, abstractmethod

class BaseProcessor(ABC):

    @staticmethod
    def add_default_args(parser:ArgumentParser):

        parser.add_argument("--dates", help="Dates from which to query and load submissions")
        parser.add_argument("--count-init-contests", help="Amount of contests that should be processed during the initial run",default=40)

        # namespace, _ = parser.parse_known_args()
        #
        # dates = None
        # if "dates" in namespace:
        #     dates = namespace.dates
        #
        # count_init_contests = 40
        # if "count_init_contests" in namespace:
        #     count_init_contests = int(namespace.count_init_contests) if namespace.count_init_contests.isdigit() else 40
        #
        # return dates, count_init_contests
    @staticmethod
    def query_api(url, headers = {}, **params):
        if params:
            url = url + "?"

            for param, value in params.items():
                url += param + "=" + value + "&"

        resp = requests.get(url=url, headers=headers)
        return resp

    @staticmethod
    def process_response(response):
        print(response.status_code)
        print(response.reason)

        converted_response = json.loads(response.content.decode("utf-8"))
        return converted_response

    @staticmethod
    def translate_unix_to_timestamp(unix_time):
        timestamp = dt.datetime.fromtimestamp(unix_time)
        return timestamp

    @staticmethod
    def parse_dates(dates, date_format="%Y-%m-%d") -> (dt.date | None, dt.date | None):

        if not dates:
            return None, None

        date_str_split = dates.split(":")
        if len(date_str_split) < 2:
            return None, None

        try:
            from_date = dt.datetime.strptime(date_str_split[0], date_format).date()
            to_date = dt.datetime.strptime(date_str_split[1], date_format).date()
        except ValueError as ve:
            print(f"Wasn't able to get the dates provided because of the following error -> {str(ve)}")
            return None, None

        if from_date > to_date:
            return to_date, from_date

        return from_date, to_date

    # Class methods
    @abstractmethod
    def write_to_db(self, data, mode, table_name):
        pass

    @abstractmethod
    def read_from_db(self, query):
        pass

    @abstractmethod
    def execute_sql(self, sql_statement: str):
        pass

    @abstractmethod
    def load_last_execution_date(self) -> dt.date:
        pass


    @staticmethod
    def process_contest(
            contest,
            from_date = None,
            to_date = None,
            amount_of_contests = 40
    ):

        min_id = int(contest["max_index"]) - int(amount_of_contests)

        # Initial Run
        # if initial and contest["id"] > min_id \
        #     and contest["phase"] == "FINISHED" \
        #     and self.translate_unix_to_timestamp(contest["startTimeSeconds"] + contest["durationSeconds"]).date() < to_date:
        if from_date is None:
            contest_start_time = BaseProcessor.translate_unix_to_timestamp(contest["startTimeSeconds"])
            contest_end_time = BaseProcessor.translate_unix_to_timestamp(contest["startTimeSeconds"] + contest["durationSeconds"])

            if contest["id"] > min_id \
                    and contest["phase"] == "FINISHED"\
                    and contest_end_time.date() < to_date:
                return {
                    "id": contest["id"],
                    "name": contest["name"],
                    "start": contest_start_time,
                    "end": contest_end_time,
                    "duration": contest["durationSeconds"],
                    "type": contest["type"]
                }

        # Manual Parameters provided
        elif from_date is not None and to_date is not None:
            contest_start_time = BaseProcessor.translate_unix_to_timestamp(contest["startTimeSeconds"])
            contest_end_time = BaseProcessor.translate_unix_to_timestamp(contest["startTimeSeconds"] + contest["durationSeconds"])
            if (
                    from_date <= contest_end_time.date() < to_date
                    and contest["phase"] == "FINISHED"
                    # and contest["id"] > min_id
            ):

                return {
                    "id": contest["id"],
                    "name": contest["name"],
                    "start": contest_start_time,
                    "end": contest_end_time,
                    "duration": contest["durationSeconds"],
                    "type": contest["type"]
                }
        # else:
        #     raise Exception("Incorrect combination of attributes for loading contests!")

        # self.write_to_db(data=lst_of_rows, mode="overwrite", table_name = "contest_stg")
        #
        # return [row[0] for row in lst_of_rows]
        return {}


    @staticmethod
    def extract_submissions(contest_id):
        sumbissions = BaseProcessor.establish_connection("https://codeforces.com/api/contest.status", contestId=str(contest_id))
        contest_sumbissions = [
            {
                "id": subm["id"],
                "timestamp": BaseProcessor.translate_unix_to_timestamp(subm["creationTimeSeconds"]),
                "id_contest": subm["contestId"],
                "id_problem": str(subm["problem"]["contestId"]) + "/" + str(subm["problem"]["index"]),
                "problem_name": subm["problem"]["name"],
                "tags": ",".join(subm["problem"]["tags"]),
                "author": subm["author"]["members"][0].get("handle", "unknown") if subm["author"]["members"] else "unknown",
                "programming_language": subm["programmingLanguage"],
                "verdict": subm["verdict"],
                "time_consumed": subm["timeConsumedMillis"],
                "memory_usage": subm["memoryConsumedBytes"]
            }

            for subm in sumbissions
        ]

        print("Submissions Extracted!")
        return contest_sumbissions

    @staticmethod
    def handle_error_response(response, api_params):
        if "handles: User with handle" in response.get("comment"):
            users = api_params["handles"] \
                .replace("&", "") \
                .split(";")

            comment_as_list = response.get("comment").split(" ")
            incorrect_user = comment_as_list[comment_as_list.index("handle") + 1]

            users.remove(incorrect_user)
            # sys.exit(0)
            return {"handles": ";".join(users)}
        else:
            print(f"Action on the following response {response} is not implemented yet!")

    @staticmethod
    def establish_connection(url, **api_params):
        exception = None
        retry = 0
        while retry < 3:
            api_response = ""
            try:
                logging.info("Establishing connection to the API!")
                api_response = BaseProcessor.query_api(url, **api_params)
                response = BaseProcessor.process_response(api_response)
                if response and "result" not in response:
                    api_params = BaseProcessor.handle_error_response(response, api_params)
                    continue
                else:
                    entities = response["result"]

                return entities
            except json.decoder.JSONDecodeError as e:
                exception = e
                time.sleep(15)
                logging.error(f"{e} error occured")
                logging.error(f"Response from the API -> {str(api_response)}")
                retry += 1
                continue
            except requests.exceptions.ConnectionError as e:
                exception = e
                time.sleep(15)
                logging.error(f"{e} error occured")
                logging.error(f"Response from the API -> {str(api_response)}")
                retry += 1
                continue
            except Exception as e:
                exception = e
                time.sleep(15)
                logging.error(f"{e} error occured")
                logging.error(f"Response from the API -> {str(api_response)}")
                retry += 1
                continue

        if retry == 3:
            raise exception

    @staticmethod
    def extract_users(rows):
        unique_names_string = ";".join(rows)

        raw_rows = BaseProcessor.establish_connection("https://codeforces.com/api/user.info", handles=unique_names_string)

        unpacked_rows = [
            {
                "country": raw_row.get("country", "unknown"),
                "rating": raw_row.get("rating", 0),
                "nickname": raw_row["handle"],
                "title": raw_row.get("rank", "none"),
                "registration_date": BaseProcessor.translate_unix_to_timestamp(raw_row["registrationTimeSeconds"])
            }
            for raw_row in raw_rows
        ]

        return unpacked_rows

    # @abstractmethod
    # def prepare_auto_increment_data(self, data):
    #     pass

    # def load_dimensions(self):
    #     # Load problems
    #     problems_data = self.read_from_db("SELECT DISTINCT id_problem, problem_name AS name, tags FROM load_submissions")
    #     self.write_to_db(data=problems_data, mode="overwrite", table_name="problem_stg")
    #
    #     # Load programming languages
    #     programming_languages_data = self.read_from_db("SELECT DISTINCT programming_language FROM load_submissions")
    #
    #     prog_lang_prepared = self.prepare_auto_increment_data(programming_languages_data)
    #     self.write_to_db(data=prog_lang_prepared, mode="overwrite", table_name="programming_language_stg")
    #
    #     # Load verdicts
    #     verdicts_df = self.read_from_db("SELECT DISTINCT verdict FROM load_submissions")
    #     verdicts_prepared = self.prepare_auto_increment_data(verdicts_df)
    #     self.write_to_db(data=verdicts_prepared, mode="overwrite", table_name="verdict_stg")


    # def load_users(self):
    #     unique_names = [row.author for row in self.read_from_db("SELECT DISTINCT author FROM load_submissions").collect()]
    #     self.execute_sql("TRUNCATE TABLE user_stg")
    #     print("Entering the load users function")
    #
    #     rows = []
    #     for i, name in enumerate(unique_names):
    #
    #         rows.append(name)
    #
    #         if (i!=0 and i%500== 0) or (i == len(unique_names)-1):
    #             unique_names_string = ";".join(rows)
    #             # print("Sleeping....")
    #             # time.sleep(1)
    #             raw_rows = self.establish_connection("https://codeforces.com/api/user.info", handles=unique_names_string)
    #             rows = []
    #
    #             unpacked_rows = [
    #                 (
    #                     raw_row.get("country", "unknown"),
    #                     raw_row.get("rating", 0),
    #                     raw_row["handle"],
    #                     raw_row.get("rank", "none"),
    #                     BaseProcessor.translate_unix_to_timestamp(raw_row["registrationTimeSeconds"])
    #                 )
    #                 for raw_row in raw_rows
    #             ]
    #
    #             # mode = "overwrite" if i == 500 or i == len(unique_names)-1 else "append"
    #             # df_users = spark.createDataFrame(unpacked_rows, schema=user_schema).withColumn("id", lit(0))
    #             self.write_to_db(data=unpacked_rows, mode="append", table_name="user_stg")



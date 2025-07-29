import datetime as dt
from .BaseProcessor import BaseProcessor
import boto3

class AWSProcessor(BaseProcessor):
    def __init__(
            self,
            workgroup_name,
            db_name,
            secret_arn
    ):
        # Default clients for simple interaction with the Redshift
        self._client = boto3.client(
            "redshift-data"
        )
        self._client_execution_config = {
            "WorkgroupName": workgroup_name,
            "Database":db_name,
            "SecretArn":secret_arn
        }

        self.db_name = db_name
        self._date_format="%Y-%m-%d"


    def write_to_db(self, data, mode, table_name):
        pass

    def _wait_for_query_completion(self, execution_id):
        execution_info = self._client.describe_statement(Id=execution_id)

        while execution_info["Status"] != "FINISHED" and execution_info["Status"] != "FAILED":
            execution_info = self._client.describe_statement(Id=execution_id)

        return execution_info

    def _get_query_result(self, execution_id) -> list:

        statement = self._client.get_statement_result(Id=execution_id)

        processed_statement = []
        for i in range(len(statement["Records"])):
            record = {}
            for j in range(len(statement["ColumnMetadata"])):
                record[statement["ColumnMetadata"][j]["label"]] = list(statement["Records"][i][j].values())[0]

            processed_statement.append(record)

        return processed_statement

    def read_from_db(self, query) -> list:
        response = self._client.execute_statement(
            **self._client_execution_config,
            Sql = query
        )
        execution_info = self._wait_for_query_completion(response["Id"])
        print(f"STATUS: {execution_info['Status']}; {execution_info['Error']};") if execution_info["Status"] == "FAILED" else print(f"STATUS: {execution_info['Status']}")

        if execution_info['Status'] == "FAILED":
            raise Exception(f"Job with the following ID -> {execution_info['Id']}, failed with the following error -> {execution_info['Error']}")

        return self._get_query_result(response["Id"])

    def execute_sql(self, sql_statement: str):
        response = self._client.execute_statement(
            **self._client_execution_config,
            Sql = sql_statement
        )
        execution_info = self._wait_for_query_completion(response["Id"])

        if "Error" in execution_info:
            raise Exception(f"The following error has occurred -> {execution_info['Error']} during the execution of the following query -> {sql_statement}")

        return execution_info

    def load_last_execution_date(self) -> [dt.date | None]:

        query = "SELECT * FROM last_execution LIMIT 1;"
        query_result = self.read_from_db(query)

        if not query_result:
            return None

        last_execution_date = query_result[0]["last_execution_date"]
        last_execution_date_formatted = dt.datetime.strptime(last_execution_date, self._date_format).date()
        return last_execution_date_formatted
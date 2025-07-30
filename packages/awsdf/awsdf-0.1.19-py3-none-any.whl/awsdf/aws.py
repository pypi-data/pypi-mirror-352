"""
This module enables connecting to AWS and extracting metadata in pandas dataframes.

**Installing from PyPI:** *pip install -U awsdf*

**USAGE:**

    import awsdf

    aws_account = awsdf.Account(profile_name="<PROFILE_NAME>")

    glue_databases_df = aws_account.glue_get_databases()

"""
from datetime import timedelta, datetime
from awswrangler import exceptions
import boto3
import botocore
import botocore.exceptions
from loguru import logger
import numpy as np
import pandas as pd
import awswrangler as wr
from pandas.core.frame import DataFrame
from botocore.exceptions import ClientError
from tqdm import tqdm
import base64
import json

AWS_SFN_CLIENT = "stepfunctions"
AWS_GLUE_CLIENT = "glue"
AWS_EMR_CLIENT = "emr"
AWS_ATHENA_CLIENT = "athena"
AWS_LAMBDA_CLIENT = "lambda"
AWS_EC2_CLIENT = "ec2"
AWS_ECS_CLIENT = "ecs"
AWS_CLOUDWATCH_CLIENT = "cloudwatch"
AWS_S3_CLIENT = "s3"
AWS_QUICKSIGHT_CLIENT = "quicksight"

COL_DBNAME = "DBName"
COL_TABLENAME = "table_name"
COL_CREATEDATETIME = "CreateTime"
COL_UPDATEDATETIME = "UpdateTime"
COL_TABLETYPE = "TableType"
COL_CREATEDBY = "CreatedBy"
DF_TABLECOLUMNS = [
    COL_DBNAME,
    COL_TABLENAME,
    COL_CREATEDATETIME,
    COL_UPDATEDATETIME,
    COL_TABLETYPE,
    COL_CREATEDBY,
]
COL_FIELDNAME = "field_name"
COL_FIELDTYPE = "field_type"

DURATION_COL_NAME = "executiontime"
AVG_DURATION_COL_NAME = "Estimated duration (Avg mins)"


def keyexists(key, dictionary):
    return True if key in dictionary else False


def get_value(key, obj):
    return obj[key] if key in obj else None


error_df = pd.DataFrame(columns=["Error"], data=[[-1]])
tqdm.pandas()


class Account(object):
    """
    Instantiate class object for connecting to AWS and retriving metadata from AWS
    """

    def __init__(
        self,
        aws_access_key_id=None,
        aws_secret_access_key=None,
        aws_session_token=None,
        region_name=None,
        profile_name=None,
    ):
        """
        Provide access keys OR Profile name to connect to AWS account. Keys take preceedence

        **Parameters:**

            *aws_access_key_id (string) -- AWS access key ID*

            *aws_secret_access_key (string) -- AWS secret access key*

            *aws_session_token (string) -- AWS temporary session token*

            *region_name (string) -- AWS region*

            *profile_name (string) -- AWS profile name*
        """
        try:
            self._session = boto3.Session(
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
                aws_session_token=aws_session_token,
                region_name=region_name,
                profile_name=profile_name,
            )
        except botocore.exceptions.ProfileNotFound as error:
            print(error)
            exit(0)
        except botocore.exceptions.BotoCoreError as error:
            print("Exception while creating boto3 session.")
            logger.error(error)
            exit(0)

        self._region = self._session.region_name
        self._accountid = self.iam_get_accountid()

    @property
    def session(self):
        return self._session

    @property
    def region(self):
        return self._region

    @property
    def accountid(self):
        return self._accountid

    def iam_get_accountid(self) -> str:
        try:
            return wr.sts.get_account_id(self.session)
        except botocore.exceptions.ClientError as error:
            print(
                f"{error.response['Error']['Code']}:{error.response['Error']['Message']}"
            )
            exit(0)
        except botocore.exceptions.UnauthorizedSSOTokenError as error:
            print(error)
            logger.error(error)
            exit(0)
        except botocore.exceptions.BotoCoreError as error:
            print("Exception while getting accountid.")
            logger.error(error)
            exit(0)

    def glue_get_jobs(self) -> pd.DataFrame:
        """
        Get AWS Glue jobs

        Returns:
            dataframe
        """
        glue_job_df_columns = ["Name", "CreatedOn", "LastModifiedOn"]

        # initialize Glue client
        client = self.session.client(AWS_GLUE_CLIENT)
        paginator = client.get_paginator("get_jobs")

        page_iterator = paginator.paginate()

        data = []
        for page in page_iterator:
            for job in page["Jobs"]:
                data.append([job["Name"], job["CreatedOn"], job["LastModifiedOn"]])

        jobs_df = pd.DataFrame(data, columns=glue_job_df_columns)
        # localize dates to remove timezone; writing to excel with timezone is not supported
        jobs_df["CreatedOn"] = jobs_df["CreatedOn"].dt.tz_localize(None)
        jobs_df["LastModifiedOn"] = jobs_df["LastModifiedOn"].dt.tz_localize(None)

        return jobs_df

    def glue_get_job_history(self, job_name, no_of_runs=1) -> pd.DataFrame:
        """
        Retrieve glue job history

        Arguments:
            job_name -- Name of job to retrive history

        Keyword Arguments:
            no_of_runs -- No of runs to retrive in descending order (default: {1})

        Returns:
            dataframe
        """

        glue_run_df_columns = [
            "Id",
            "JobName",
            "JobRunState",
            "StartedOn",
            "stopDate",
            DURATION_COL_NAME,
            "MaxCapacity",
            "WorkerType",
            "NumberOfWorkers",
            "GlueVersion",
        ]

        data = []
        # initialize Glue client
        client = self.session.client(AWS_GLUE_CLIENT)
        paginator = client.get_paginator("get_job_runs")

        page_iterator = paginator.paginate(JobName=job_name)

        # Assumes data is returned in descending order of Job StartedOn Date
        for page in page_iterator:
            for jobrun in page["JobRuns"]:
                completedon_value = (
                    jobrun["CompletedOn"]
                    if keyexists("CompletedOn", jobrun)
                    else jobrun["StartedOn"]
                )
                # TODO: Optimize below logic
                stop_date = (
                    None if jobrun["JobRunState"] == "RUNNING" else completedon_value
                )
                data.append(
                    [
                        jobrun["Id"],
                        jobrun["JobName"],
                        jobrun["JobRunState"],
                        jobrun["StartedOn"],
                        stop_date,
                        jobrun["ExecutionTime"],
                        jobrun["MaxCapacity"],
                        jobrun["WorkerType"]
                        if keyexists("WorkerType", jobrun)
                        else np.nan,
                        jobrun["NumberOfWorkers"]
                        if keyexists("NumberOfWorkers", jobrun)
                        else np.nan,
                        jobrun["GlueVersion"]
                        if keyexists("GlueVersion", jobrun)
                        else np.nan,
                    ]
                )

        job_run_df = pd.DataFrame(data, columns=glue_run_df_columns)
        job_run_df.sort_values(["StartedOn"], ascending=False, inplace=True)
        avg_duration = (
            job_run_df[job_run_df["JobRunState"] == "SUCCEEDED"]
            .sort_values(["StartedOn"], ascending=False)
            .head()[DURATION_COL_NAME]
            .mean()
        )
        job_run_df[AVG_DURATION_COL_NAME] = avg_duration

        job_run_df.rename(
            columns={"JobRunState": "status", "StartedOn": "startDate"}, inplace=True
        )

        final_df = None
        if no_of_runs > 0:
            final_df = job_run_df.head(no_of_runs).loc[
                :,
                [
                    "JobName",
                    "status",
                    "startDate",
                    "stopDate",
                    DURATION_COL_NAME,
                    "MaxCapacity",
                    "WorkerType",
                    "NumberOfWorkers",
                    "GlueVersion",
                ],
            ]
        else:
            final_df = job_run_df.loc[
                :,
                [
                    "JobName",
                    "status",
                    "startDate",
                    "stopDate",
                    DURATION_COL_NAME,
                    "MaxCapacity",
                    "WorkerType",
                    "NumberOfWorkers",
                    "GlueVersion",
                ],
            ]

        if not final_df.empty:
            final_df["startDate"] = final_df["startDate"].dt.tz_localize(None)
            final_df["stopDate"] = final_df["stopDate"].dt.tz_localize(None)

        return final_df

    def glue_get_databases(self) -> pd.DataFrame:
        """
        Get AWS Glue jobs

        Returns:
            dataframe
        """
        dbs = wr.catalog.get_databases(boto3_session=self.session)
        data = [(db["Name"]) for db in dbs]
        databases_df = pd.DataFrame(data, columns=[COL_DBNAME])
        return databases_df

    def glue_get_tables(self, dbname=None) -> pd.DataFrame:
        """
        Get AWS Glue tables

        Keyword Arguments:
            dbname -- Database Name for which to retrieve tables (default: {None})

        Returns:
            dataframe
        """
        tables = wr.catalog.get_tables(database=dbname, boto3_session=self.session)

        data = [
            (
                table["Name"],
                get_value("CreateTime", table),
                get_value("UpdateTime", table),
                get_value("TableType", table),
                get_value("CreatedBy", table),
            )
            for table in tables
        ]

        tables_df = pd.DataFrame(
            data,
            columns=[
                COL_TABLENAME,
                COL_CREATEDATETIME,
                COL_UPDATEDATETIME,
                COL_TABLETYPE,
                COL_CREATEDBY,
            ],
        )
        return tables_df

    def glue_get_fields(self, dbname, tablename) -> pd.DataFrame:
        """
        Get AWS Glue table columns

        Keyword Arguments:
            dbname -- Database Name for table
            tablename -- Database Name for which to retrieve columns

        Returns:
            dataframe
        """
        dict_columns = wr.catalog.get_table_types(
            database=dbname, table=tablename, boto3_session=self.session
        )

        df_data = []
        for key in dict_columns:
            df_data.append([tablename, key, dict_columns[key]])

        column_names = [COL_TABLENAME, COL_FIELDNAME, COL_FIELDTYPE]
        df_columns = pd.DataFrame(columns=column_names, data=df_data)
        # print(df_columns.head())
        return df_columns

    def athena_execute_query(self, database: str, query: str, use_cache: bool = True):
        """
        Execute athena query

        Arguments:
            database -- Database name
            query -- Query to execute

        Keyword Arguments:
            use_cache -- Use cached results if any (default: {True})

        Returns:
            dataframe
        """
        logger.info("Query execution started")
        max_cache_seconds = 172800
        if not use_cache:
            max_cache_seconds = 0
        athena_cache_settings = {
            "max_cache_seconds": max_cache_seconds,
        }
        query_df = None
        try:
            logger.debug("Query execution started")
            query_df = wr.athena.read_sql_query(
                query,
                database=database,
                ctas_approach=False,
                boto3_session=self.session,
                athena_cache_settings=athena_cache_settings,
            )
        except exceptions.QueryFailed as error:
            # TODO: log Query execution error
            print(f"Error executing query for table: {exceptions.QueryFailed.__name__}")
            raise error
        except botocore.exceptions.ClientError as error:
            # TODO: log Query execution error
            print(
                f"{error.response['Error']['Code']}:{error.response['Error']['Message']}"
            )
            raise error

        logger.debug("Query execution ended")
        logger.info("Query execution complete")

        return query_df

    def athena_get_view_definition(
        self, database: str, viewname: str, query_location: str
    ):
        client_athena: boto3.client = self.session.client(AWS_ATHENA_CLIENT)

        query = f"""
        show create view {database}.{viewname}
        """

        response = client_athena.start_query_execution(
            QueryString=query,
            QueryExecutionContext={"Database": database},
            ResultConfiguration={
                "OutputLocation": query_location,
            },
            WorkGroup="primary",
        )

        executionid = response["QueryExecutionId"]
        logger.debug(executionid)

        response = client_athena.get_query_execution(QueryExecutionId=executionid)
        OutputLocation = response["QueryExecution"]["ResultConfiguration"][
            "OutputLocation"
        ]
        logger.debug(OutputLocation)

        client_s3: boto3.client = self.session.client(AWS_S3_CLIENT)

        arr_split = str(OutputLocation).split(sep="/", maxsplit=3)
        bucket = arr_split[2]
        key = arr_split[3]
        logger.debug(f"bucket={bucket}; key={key}")

        self.s3_wait_check_object_exists(bucket_name=bucket, key_name=key)

        s3_object = client_s3.get_object(Bucket=bucket, Key=key)
        body = s3_object["Body"]

        return body.read()

    def athena_create_table(
        self,
        dataframe_to_upload: pd.DataFrame,
        table_name: str,
        s3_path: str,
        database="qdl_temp",
        mode="overwrite",
    ):
        try:
            session = self.session
            wr.s3.to_parquet(
                df=dataframe_to_upload,
                path=s3_path,
                dataset=True,
                mode=mode,
                database=database,
                table=table_name,
                boto3_session=session,
            )
        except botocore.exceptions.UnauthorizedSSOTokenError as error:
            logger.error(error)

        logger.debug("Athena table created successfully.")

    def athena_data_dictionary(
        self, include_dbs: list = [], exclude_dbs: list = []
    ) -> pd.DataFrame:
        """
        Get AWS Athean data dictionary. A data frame with all databases, tables & fields with datatypes

        Keyword Arguments:
            include_dbs (optional) -- list of databases to be included
            exclude_dbs (optional) -- list of databases to be excluded if include_dbs list is empty.

        Returns:
            dataframe
        """
        # Get glue databases
        databases_df = self.glue_get_databases()

        # create list of databases and loop to retrieve all fields
        lst_databases = databases_df[COL_DBNAME].tolist()

        final_tables_df = pd.DataFrame(columns=DF_TABLECOLUMNS)
        final_fields_df = pd.DataFrame(
            columns=[COL_DBNAME, COL_TABLENAME, COL_FIELDNAME, COL_FIELDTYPE]
        )
        lst_tqdm = tqdm(lst_databases)
        for db in lst_tqdm:
            lst_tqdm.set_description(f"Processing database: {db}")
            if len(include_dbs) > 0:
                if not db in include_dbs:
                    continue
            elif len(include_dbs) == 0 and len(exclude_dbs) > 0:
                if db in exclude_dbs:  # These databases are not required
                    continue

            tables_df = self.glue_get_tables(dbname=db)
            tables_df.insert(0, COL_DBNAME, db, allow_duplicates=True)

            # Get fields for tables
            lst_tables = tables_df[COL_TABLENAME].tolist()
            for table in lst_tables:
                fields_df = self.glue_get_fields(dbname=db, tablename=table)
                fields_df.insert(0, COL_DBNAME, db, allow_duplicates=True)
                # print(fields_df.head())

                final_fields_df = pd.concat([final_fields_df, fields_df])

            final_tables_df = pd.concat([final_tables_df, tables_df])

        # Merge tables & fields
        print(f"Shape before fields merge: {final_tables_df.shape}")
        final_tablesAndFields_df = pd.merge(
            final_tables_df, final_fields_df, how="left", on=[COL_DBNAME, COL_TABLENAME]
        )
        print(f"Shape after fields merge: {final_tables_df.shape}")

        # TODO: Check duplicates here
        # duplicate_count = final_df.duplicated(subset=[COL_DBNAME, COL_TABLENAME]).sum()
        # if duplicate_count > 0:
        #     print(f"Duplicate tables found. Duplicate count = {duplicate_count}")
        #     exit(0)
        # else:
        #     print(f"No duplicate tables.")

        # localize dates to remove timezone; writing to excel with timezone is not supported
        # final_tablesAndFields_df[COL_CREATEDATETIME] = final_tablesAndFields_df[COL_CREATEDATETIME].dt.tz_localize(
        #     None)
        # final_tablesAndFields_df[COL_UPDATEDATETIME] = final_tablesAndFields_df[COL_UPDATEDATETIME].dt.tz_localize(
        #     None)

        # final_df.to_csv("dl_datadictionary.csv", index=False)
        return final_tablesAndFields_df

    def lambda_get_functions(self):
        dataframe_columns = [
            "arn",
            "name",
            "codesize",
            "description",
            "timeout",
            "memorysize",
            "lastmodified",
            "version",
        ]
        client_lambda: boto3.client = self.session.client(AWS_LAMBDA_CLIENT)
        paginator = client_lambda.get_paginator("list_functions")
        page_iterator = paginator.paginate()

        data = []

        for page in page_iterator:
            for func in page["Functions"]:
                row = [
                    func["FunctionArn"],
                    func["FunctionName"],
                    func["CodeSize"],
                    func["Description"],
                    func["Timeout"],
                    func["MemorySize"],
                    func["LastModified"],
                    func["Version"],
                ]
                data.append(row)

        functions_df = pd.DataFrame(data, columns=dataframe_columns)
        return functions_df

    def lambda_get_metrics_list(self, namespace="AWS/Lambda"):
        # TODO: this is incomplete
        logger.debug("Retrieving lambda metrics list")
        client_cloudwatch: boto3.client = self.session.client(AWS_CLOUDWATCH_CLIENT)
        paginator = client_cloudwatch.get_paginator("list_metrics")
        page_iterator = paginator.paginate(Namespace=namespace)

        dataframe_columns = [
            "Namespace",
            "MetricName",
            "DimensionName",
            "DimensionValue",
        ]
        data = []
        for page in page_iterator:
            # print(page)
            for metric in page["Metrics"]:
                for dimension in metric["Dimensions"]:
                    row = [
                        (
                            metric["Namespace"],
                            metric["MetricName"],
                            dimension["Name"],
                            dimension["Value"],
                        )
                    ]
                    data.append(row)
            # break
        metrics_df = pd.DataFrame(row, columns=dataframe_columns)
        return metrics_df

    def lambda_get_invocations(self, lambda_name, start_date=None, end_date=None):
        sdate = (
            datetime.now() - timedelta(days=30) if start_date is None else start_date
        )
        edate = datetime.now() if end_date is None else end_date

        logger.debug(f"Retrieving invocations for lambda={lambda_name}")
        client_cloudwatch: boto3.client = self.session.client(AWS_CLOUDWATCH_CLIENT)
        paginator = client_cloudwatch.get_paginator("get_metric_data")
        page_iterator = paginator.paginate(
            MetricDataQueries=[
                {
                    "Id": "myrequest",
                    "MetricStat": {
                        "Metric": {
                            "Namespace": "AWS/Lambda",
                            "MetricName": "Invocations",
                            "Dimensions": [
                                {"Name": "FunctionName", "Value": lambda_name},
                            ],
                        },
                        "Period": 86400,
                        "Stat": "Sum",
                    },
                },
            ],
            StartTime=sdate,
            EndTime=edate,
        )

        dataframe_columns = ["FunctionName", "Timestamps", "Values"]
        data = []

        for page in page_iterator:
            for metric_data_result in page["MetricDataResults"]:
                if metric_data_result["Id"] == "myrequest":
                    datapoints = [
                        (
                            metric_data_result["Timestamps"][i],
                            metric_data_result["Values"][i],
                        )
                        for i in range(0, len(metric_data_result["Timestamps"]))
                    ]
                    for datapoint in datapoints:
                        row = [lambda_name, datapoint[0], datapoint[1]]
                        data.append(row)

        metric_data_df = pd.DataFrame(data, columns=dataframe_columns)

        logger.debug(f"Dataframe shape is {metric_data_df.shape}")
        return metric_data_df

    def sfn_get_statemachines(self):
        dataframe_columns = ["arn", "name", "type", "creationDate"]
        client_lambda: boto3.client = self.session.client(AWS_SFN_CLIENT)
        paginator = client_lambda.get_paginator("list_state_machines")
        page_iterator = paginator.paginate()

        data = []
        for page in page_iterator:
            for statemachine in page["stateMachines"]:
                row = [
                    statemachine["stateMachineArn"],
                    statemachine["name"],
                    statemachine["type"],
                    statemachine["creationDate"],
                ]
                data.append(row)

        stepfunctions_df = pd.DataFrame(data, columns=dataframe_columns)
        return stepfunctions_df

    def get_available_profiles(self) -> list[str]:
        return self.session.available_profiles

    def ec2_get_instance_id(self, hostname):
        df_columns = [
            "InstanceId",
            "InstanceType",
            "KeyName",
            "LaunchTime",
            "PublicDnsName",
            "State",
        ]
        client_ec2: boto3.client = self.session.client(AWS_EC2_CLIENT)
        paginator = client_ec2.get_paginator("describe_instances")
        page_iterator = paginator.paginate(
            Filters=[
                {
                    "Name": "tag:Name",
                    "Values": [
                        hostname,
                    ],
                },
            ],
        )

        data = []
        for page in page_iterator:
            for ec2_instances in page["Reservations"]:
                # print(ec2Instances['Instances'])
                for instance in ec2_instances["Instances"]:
                    row = [
                        instance["InstanceId"],
                        instance["InstanceType"],
                        instance["KeyName"],
                        instance["LaunchTime"],
                        instance["PublicDnsName"],
                        instance["State"]["Name"],
                    ]
                    data.append(row)

        ec2_instances_df = pd.DataFrame(data, columns=df_columns)

        return (
            ec2_instances_df["InstanceId"].iloc[0]
            if not ec2_instances_df.empty
            else None
        )

    def ec2_get_instanceip(self, ec2_instance_id):
        client_ec2: boto3.client = self.session.resource(AWS_EC2_CLIENT)

        instance = client_ec2.Instance(ec2_instance_id)
        return instance.private_ip_address

    def ecs_get_clusters(self) -> pd.DataFrame:
        client_ecs: boto3.client = self.session.client(AWS_ECS_CLIENT)
        paginator = client_ecs.get_paginator("list_clusters")
        page_iterator = paginator.paginate()

        lst_cluster_arns = []
        for page in page_iterator:
            lst_cluster_arns.extend(page["clusterArns"])

        df_columns = ["clusterArn"]
        clusters_df = pd.DataFrame(lst_cluster_arns, columns=df_columns)
        logger.debug(f"Shape of clusters df={clusters_df.shape}")
        return clusters_df

    def ecs_get_services(self, cluster_arn) -> pd.DataFrame:
        client_ecs: boto3.client = self.session.client(AWS_ECS_CLIENT)
        paginator = client_ecs.get_paginator("list_services")
        page_iterator = paginator.paginate(cluster=cluster_arn)

        lst_service_arns = []
        for page in page_iterator:
            lst_service_arns.extend(page["serviceArns"])

        df_columns = ["serviceArn"]
        services_df = pd.DataFrame(lst_service_arns, columns=df_columns)

        services_df.insert(loc=0, column="clusterArn", value=cluster_arn)
        # logger.debug(
        #     f"Services for cluster={clusterARN} is {services_df.shape}")

        return services_df

    def ecs_get_tasks(self, cluster_arn, service_arn):
        client_ecs: boto3.client = self.session.client(AWS_ECS_CLIENT)
        paginator = client_ecs.get_paginator("list_tasks")
        page_iterator = paginator.paginate(
            cluster=cluster_arn, serviceName=service_arn, desiredStatus="RUNNING"
        )
        lst_task_arns = []
        for page in page_iterator:
            lst_task_arns.extend(page["taskArns"])

        df_columns = ["taskArn"]
        tasks_df = pd.DataFrame(lst_task_arns, columns=df_columns)

        tasks_df.insert(loc=0, column="clusterArn", value=cluster_arn)
        tasks_df.insert(loc=1, column="serviceArn", value=service_arn)

        logger.debug(
            f"Tasks for cluster={cluster_arn} & Service={service_arn} is"
            f" {tasks_df.shape}"
        )

        return tasks_df

    def ecs_get_allservices(self) -> pd.DataFrame:
        custers_df = self.ecs_get_clusters()

        lst_clusers = custers_df["clusterArn"].to_list()

        all_services_df = pd.DataFrame(columns=["clusterArn", "serviceArn"])
        tqdm_cluster = tqdm(lst_clusers)
        tqdm_cluster.set_description("Gathering ecs clusters & services metadata")
        for cluster in tqdm_cluster:
            services_df = self.ecs_get_services(cluster_arn=cluster)
            all_services_df = pd.concat([all_services_df, services_df])

        # logger.debug(f"Shape of all services df={all_services_df.shape}")

        # validation: Ensure service ARNs are not duplicated
        if services_df.duplicated(subset=["serviceArn"]).sum() > 0:
            logger.warning("Duplicate service ARNs found.")
        else:
            logger.info("Service ARN's are unique")

        # # Loop thorugh all rows and get task details
        # all_tasks_df = pd.DataFrame(
        #     columns=['clusterArn', 'serviceArn', 'taskArn'])
        # for index, row in all_services_df.iterrows():
        #     logger.debug(row["clusterArn"], row["serviceArn"])
        #     task_df = self.get_ecs_tasks(row["clusterArn"], row["serviceArn"])
        #     all_tasks_df = pd.concat([all_tasks_df, task_df])
        #     # print(task_df.head())
        #     # break

        return all_services_df

    def ecs_get_container_instance(self, cluster_arn, task_arn):
        client_ecs: boto3.client = self.session.client(AWS_ECS_CLIENT)
        response = client_ecs.describe_tasks(
            cluster=cluster_arn,
            tasks=[
                task_arn,
            ],
        )
        # print(response)
        if len(response["tasks"]) > 1:
            logger.error("Multiple task found. Exiting")
            exit(0)
        else:
            return response["tasks"][0]["containerInstanceArn"]

    def ecs_get_container_ec2_instanceid(self, cluster_arn, container_instance):
        client_ecs: boto3.client = self.session.client(AWS_ECS_CLIENT)
        response = client_ecs.describe_container_instances(
            cluster=cluster_arn,
            containerInstances=[
                container_instance,
            ],
        )
        # print(response)
        if len(response["containerInstances"]) > 1:
            logger.error("Multiple container instances found. Exiting")
            exit(0)
        else:
            return response["containerInstances"][0]["ec2InstanceId"]

    def ec2_get_instances(self):
        client_ecs: boto3.client = self.session.client(AWS_EC2_CLIENT)
        paginator = client_ecs.get_paginator("describe_instances")
        page_iterator = paginator.paginate()

        df_columns = [
            "InstanceId",
            "Name",
            "ImageId",
            "InstanceType",
            "KeyName",
            "MonitoringState",
            "State",
        ]
        lst_ec2_instance_rows = []
        for page in page_iterator:
            for reservation in page["Reservations"]:
                for instance in reservation["Instances"]:
                    tag_name = [tag for tag in instance["Tags"] if tag["Key"] == "Name"]
                    row = (
                        instance["InstanceId"],
                        tag_name[0]["Value"],
                        instance["ImageId"],
                        instance["InstanceType"],
                        instance["KeyName"],
                        instance["Monitoring"]["State"],
                        instance["State"]["Name"]
                        # ,instance['Tags']
                    )
                    lst_ec2_instance_rows.append(row)

        ec2_df = pd.DataFrame(data=lst_ec2_instance_rows, columns=df_columns)
        logger.debug(f"Shape of ec2_df={ec2_df.shape}")
        return ec2_df

    def s3_wait_check_object_exists(self, bucket_name, key_name):
        session = self.session
        s3_client = session.client(AWS_S3_CLIENT)
        try:
            waiter = s3_client.get_waiter("object_exists")
            waiter.wait(
                Bucket=bucket_name,
                Key=key_name,
                WaiterConfig={"Delay": 5, "MaxAttempts": 20},
            )
            logger.debug("Object exists: " + bucket_name + "/" + key_name)
        except ClientError as error:
            raise Exception(
                "boto3 client error in use_waiters_check_object_exists: "
                + error.__str__()
            )
        except Exception as error:
            raise Exception(
                "Unexpected error in use_waiters_check_object_exists: "
                + error.__str__()
            )

    def quicksight_get_datasources(self) -> pd.DataFrame:
        """
        Get QuickSight datasources

        Keyword Arguments:
            N/A

        Returns:
            dataframe
        """

        Q_DATASOURCE_COLS = [
            "Arn",
            "DataSourceId",
            "Name",
            "Type",
            "Status",
            "CreatedTime",
            "LastUpdatedTime",
            "DataSourceParameters",
        ]
        lst_datasources = wr.quicksight.list_data_sources(boto3_session=self.session)
        datasources_df = pd.DataFrame(lst_datasources)
        datasources_df = datasources_df.loc[:, Q_DATASOURCE_COLS]
        logger.debug(f"{datasources_df.shape=}")
        return datasources_df

    def quicksight_get_datasets(self, includeDetails: bool = False) -> pd.DataFrame:
        """
        Get QuickSight datasets

        Keyword Arguments:
            includeDetails (optional) -- Include addition details i.e. ConsumedSpiceCapacityInBytes & Owner. Default=False

        Returns:
            dataframe
        """

        lst_datasets = wr.quicksight.list_datasets(boto3_session=self.session)
        datasets_df = pd.DataFrame(lst_datasets)
        COL_LIST = [
            "Arn",
            "DataSetId",
            "Name",
            "CreatedTime",
            "LastUpdatedTime",
            "ImportMode",
        ]
        if includeDetails:
            datasets_df["dataset_details_dict"] = datasets_df.progress_apply(
                lambda row: self.quicksight_get_dataset_details(row["DataSetId"]),
                axis=1,
            )
            """
            dict_keys(['Arn', 'DataSetId', 'Name', 'CreatedTime', 'LastUpdatedTime', 'PhysicalTableMap', 'LogicalTableMap', 'OutputColumns', 'ImportMode', 'ConsumedSpiceCapacityInBytes', 'FieldFolders', 'DataSetUsageConfiguration'])
            """
            datasets_df["ConsumedSpiceCapacityInBytes"] = datasets_df[
                "dataset_details_dict"
            ].apply(lambda x: x.get("ConsumedSpiceCapacityInBytes"))
            COL_LIST.append("ConsumedSpiceCapacityInBytes")

            # Get dataset permissions
            account_id = self.iam_get_accountid()
            datasets_df["Permissions"] = datasets_df.progress_apply(
                lambda row: self.quicksight_get_dataset_permissions(
                    AwsAccountId=account_id, DataSetId=row["DataSetId"]
                ),
                axis=1,
            )
            datasets_df["Owner"] = datasets_df["Permissions"].apply(
                lambda x: ",".join(
                    [str(owner["Principal"]).split("/")[-1] for owner in x]
                )
            )
            COL_LIST.append("Owner")

        datasets_df = datasets_df.loc[:, COL_LIST]
        logger.debug(f"{datasets_df.shape=}")
        return datasets_df

    def quicksight_get_dataset_permissions(self, AwsAccountId: str, DataSetId: str):
        """
        Get QuickSight dataset permissions

        Keyword Arguments:
            AwsAccountId -- AWS account id
            DataSetId -- Dataset id

        Returns:
            dataframe
        """

        client_quicksight: boto3.client = self.session.client(AWS_QUICKSIGHT_CLIENT)
        response = client_quicksight.describe_data_set_permissions(
            AwsAccountId=AwsAccountId, DataSetId=DataSetId
        )
        return response["Permissions"]

    def quicksight_get_dataset_details(self, datasetId: str) -> dict:
        """
        Get QuickSight dataset details

        Keyword Arguments:
            DataSetId -- Dataset id

        Returns:
            dataframe
        """

        # logger.debug(f"{datasetId=}")
        dataset_details_dict = dict()
        try:
            dataset_details_dict = wr.quicksight.describe_dataset(
                dataset_id=datasetId, boto3_session=self.session
            )
        except Exception as e:
            # botocore.errorfactory.InvalidParameterValueException
            if str(e).__contains__(
                "DataSet type flatFile is not supported through API yet"
            ):
                logger.warning(f"Skipping flat file dataset type. {datasetId=}")
            elif str(e).__contains__(
                "The data set type is not supported through API yet"
            ):
                logger.warning(f"Skipping unsupported dataset type {datasetId=}")
            elif str(e).__contains__(
                "DataSet type genericTable is not supported through API yet"
            ):
                logger.warning(f"Skipping genericTable dataset type {datasetId=}")
            else:
                raise Exception(e)
        return dataset_details_dict

    def quicksight_get_dashboards(self, includeDetails: bool = False) -> pd.DataFrame:
        """
        Get QuickSight dashboards

        Keyword Arguments:
            includeDetails (optional) -- **NOT IMPLEMENTED** Include addition details. Default=False

        Returns:
            dataframe
        """

        lst_dashboards = wr.quicksight.list_dashboards(boto3_session=self.session)
        dashboards_df = pd.DataFrame(lst_dashboards)
        COL_LIST = [
            "Arn",
            "DashboardId",
            "Name",
            "CreatedTime",
            "LastUpdatedTime",
            "PublishedVersionNumber",
            "LastPublishedTime",
        ]
        # if includeDetails:
        #     dashboards_df['dashboard_details_dict'] = dashboards_df.progress_apply(lambda row : self.quicksight_get_dashboard_details(row['DashboardId']), axis=1)
        #     COL_LIST.append("dashboard_details_dict")
        # print(dashboards_df.dtypes)
        # exit(0)
        dashboards_df = dashboards_df.loc[:, COL_LIST]
        logger.debug(f"{dashboards_df.shape=}")
        return dashboards_df

    def quicksight_get_dashboard_details(self, dashboardId: str) -> dict:
        """
        Get QuickSight dashboard details

        Keyword Arguments:
            dashboardId -- Dashboard id

        Returns:
            dictionary
        """

        dashboard_details_dict = wr.quicksight.describe_dashboard(
            dashboard_id=dashboardId, boto3_session=self.session
        )
        return dashboard_details_dict

    def kms_encrypt(self, plaintext: str, key_id: str) -> str:
        """
        Encrypt a plaintext string using AWS KMS and return base64-encoded ciphertext.

        Parameters:
            plaintext (str): The string to encrypt.
            key_id (str): The KMS key ARN or ID.

        Returns:
            str: base64-encoded ciphertext
        """
        kms_client = self.session.client("kms")
        try:
            response = kms_client.encrypt(
                KeyId=key_id,
                Plaintext=plaintext.encode("utf-8"),
            )
            ciphertext_blob = response["CiphertextBlob"]
            return base64.b64encode(ciphertext_blob).decode("utf-8")
        except botocore.exceptions.ClientError as e:
            logger.error(f"KMS encryption failed: {e}")
            raise e

    def kms_decrypt(self, ciphertext_b64: str) -> str:
        """
        Decrypt a base64-encoded ciphertext string using AWS KMS and return the plaintext.

        Parameters:
            ciphertext_b64 (str): base64-encoded ciphertext

        Returns:
            str: decrypted plaintext string
        """
        kms_client = self.session.client("kms")
        try:
            ciphertext_blob = base64.b64decode(ciphertext_b64)
            response = kms_client.decrypt(CiphertextBlob=ciphertext_blob)
            return response["Plaintext"].decode("utf-8")
        except botocore.exceptions.ClientError as e:
            logger.error(f"KMS decryption failed: {e}")
            raise e
        
    def get_secret_from_secrets_manager(self, secret_name: str) -> dict:
        """
        Retrieve a secret value from AWS Secrets Manager.

        Parameters:
            secret_name (str): The name or ARN of the secret.

        Returns:
            str: The secret string value.

        Raises:
            ClientError: If retrieval fails due to permission or configuration issues.
        """
        client = self.session.client(service_name='secretsmanager')

        try:
            response = client.get_secret_value(SecretId=secret_name)
            # return response["SecretString"]
            return json.loads(response["SecretString"])
        except botocore.exceptions.ClientError as e:
            logger.error(f"Error retrieving secret '{secret_name}': {e}")
            raise e        
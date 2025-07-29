import re
import logging
import os
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from urllib.parse import urlparse, urlunparse

import pandas as pd
import sqlglot

from prophecy_lineage_extractor.constants import *
from prophecy_lineage_extractor.constants import PROPHECY_URL

FILE_COUNTER = 1

def safe_env_variable(var_name):
    if var_name not in os.environ:
        logging.error(
            f"[ERROR]: Environment variable '{var_name}' is not set, Please set this value to continue."
        )
        raise Exception(f"Environment variable '{var_name}' is not set")
    return os.environ[var_name]  # Optional: return the value if needed.

def get_prophecy_name(id):
    return id.split("/")[2]

def get_safe_datasetId(datasetId):
    return str(datasetId).split("/")[2]


def get_ws_url():
    prophecy_url = safe_env_variable(PROPHECY_URL)
    try:
        # Parse the URL
        parsed_url = urlparse(prophecy_url)

        # # Ensure the URL uses HTTPS
        # if parsed_url.scheme != "https":
        #     raise ValueError("Invalid URL. Must start with 'https://'.")

        # Remove 'www.' from the netloc (hostname)
        netloc = parsed_url.netloc.replace("www.", "")

        # Create the WebSocket URL

        # Create the WebSocket URL
        websocket_url = parsed_url._replace(
            scheme="wss", netloc=netloc, path="/api/lineage/ws"
        )

        # Return the reconstructed URL without trailing slashes
        return urlunparse(websocket_url).rstrip("/")
    except Exception as e:
        raise ValueError(f"Error processing URL: {e}")


def get_graphql_url():
    prophecy_url = safe_env_variable(PROPHECY_URL)

    try:
        parsed_url = urlparse(prophecy_url)
        # # Ensure the URL uses HTTPS
        # if parsed_url.scheme not in ["https", "http"]:
        #     raise ValueError("Invalid URL. Must start with 'https://' or 'http://'.")

        # Remove 'www.' from the netloc (hostname)
        netloc = parsed_url.netloc.replace("www.", "")
        # Append '/api/md/graphql' to the path
        path = parsed_url.path.rstrip("/") + "/api/md/graphql"
        # Create the modified URL
        modified_url = parsed_url._replace(netloc=netloc, path=path)
        # Return the reconstructed URL
        return urlunparse(modified_url)

    except Exception as e:
        raise ValueError(f"Error processing URL: {e}")


def send_email(project_id, file_path: Path, pipeline_id_list = []):
    # Get SMTP credentials and email info from environment variables
    smtp_host = safe_env_variable("SMTP_HOST")
    smtp_port = int(safe_env_variable("SMTP_PORT"))  # with default values
    smtp_username = safe_env_variable("SMTP_USERNAME")
    smtp_password = safe_env_variable("SMTP_PASSWORD")
    receiver_email = safe_env_variable("RECEIVER_EMAIL")

    if not all([smtp_host, smtp_port, smtp_username, smtp_password, receiver_email]):
        raise ValueError("Missing required environment variables for SMTP or email.")

    # Create email message
    msg = MIMEMultipart()
    msg["From"] = smtp_username
    msg["To"] = receiver_email
    msg["Subject"] = (
        f"Prophecy Lineage report for Pipeline: {get_prophecy_name(project_id)}"
    )

    # Email body
    body = (
        f"Dear user,\n\tPlease find the attached Prophecy Lineage Excel report for "
        f"Project Id: {project_id}; pipeline_ids = {pipeline_id_list} \n\nThanks and regards,\n\tProphecy Team"
    )
    msg.attach(MIMEText(body, "plain"))

    # Attach Excel file
    attachment_name = file_path.name
    with open(file_path, "rb") as attachment:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header(
            "Content-Disposition", f"attachment; filename= {attachment_name}"
        )
        msg.attach(part)

    # Send email via SMTP
    try:
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(msg)
            logging.info(f"Email sent successfully to {receiver_email}")
    except Exception as e:
        logging.error(f"Failed to send email: {str(e)}")
        raise e

import json

def df_to_json_compliant_dict(df, orient='records'):
    """
    Convert a DataFrame to a JSON-compliant dictionary using pandas built-in methods.

    Args:
        df (pandas.DataFrame): DataFrame to convert
        orient (str): Orientation for dictionary conversion ('records', 'index', etc.)

    Returns:
        dict or list: JSON-compliant dictionary representation of the DataFrame
    """
    # Step 1: Replace inf/-inf with None first (pandas to_json can't handle these)
    df_cleaned = df.replace([float('inf'), float('-inf')], None)

    # Step 2: Convert to JSON string (this handles NaN/None conversions to null)
    json_str = df_cleaned.to_json(orient=orient)

    # Step 3: Parse back to Python objects (dict/list depending on orient)
    return json.loads(json_str)



def get_monitor_time():
    try:
        return int(os.environ.get(MONITOR_TIME_ENV, MONITOR_TIME_DEFAULT))
    except ValueError:
        return int(MONITOR_TIME_DEFAULT)


def debug(json_msg, msg_name=None, pause = False):
    global FILE_COUNTER
    Path("debug_jsons/").mkdir(parents=True, exist_ok=True)
    if msg_name is None:
        file_nm = f"debug_jsons/debug_file_{FILE_COUNTER}.json"
    else:
        file_nm = f"debug_jsons/debug_{msg_name}_file_{FILE_COUNTER}.json"
    with open(file_nm, "w") as fp:
        json.dump(json_msg, fp, indent=2)
    FILE_COUNTER = FILE_COUNTER + 1
    if pause:
        import pdb
        pdb.set_trace()


def convert_to_openlineage_column_transformation(row):
    """Determine transformation type and subtype based on SQL expression"""
    # Extract values from row
    sql_expr = str(row[UPSTREAM_TRANSFORMATION_COL]) if pd.notna(row[UPSTREAM_TRANSFORMATION_COL]) else row[COLNAME_COL]
    process_desc = str(row[PROCESS_DESCRIPTION]) if pd.notna(row[PROCESS_DESCRIPTION]) else ""

    # Default values
    trans_type = "INDIRECT"
    trans_subtype = "SORT"
    sql_expr_lower = sql_expr.lower()
    # DIRECT transformations
    if not sql_expr or sql_expr.strip() == '' or re.match(r'^\s*[\w\.]+\s*$', sql_expr):
        # Simple column reference or empty
        trans_type = "DIRECT"
        trans_subtype = "IDENTITY"
    elif any(agg_func in sql_expr_lower for agg_func in ["sum(", "count(", "avg(", "min(", "max(", "group by"]):
        trans_type = "DIRECT"
        trans_subtype = "AGGREGATION"
    elif any(func in sql_expr_lower for func in ["cast", "concat", "regexp", "trim", "date", "substring"]):
        trans_type = "DIRECT"
        trans_subtype = "TRANSFORMATION"
    # INDIRECT transformations
    elif "join" in sql_expr_lower:
        trans_subtype = "JOIN"
    elif "where" in sql_expr_lower or "filter" in sql_expr_lower:
        trans_subtype = "FILTER"
    elif "order by" in sql_expr_lower:
        trans_subtype = "SORT"
    elif "over(" in sql_expr_lower or "partition by" in sql_expr_lower:
        trans_subtype = "WINDOW"
    elif any(cond in sql_expr_lower for cond in ["case", "when", "if(", "coalesce"]):
        trans_subtype = "CONDITION"

    # Check for masking operations
    masking = any(mask_func in sql_expr_lower for mask_func in ["hash", "sha", "md5", "encrypt", "mask"])

    return {
        "type": trans_type,
        "subtype": trans_subtype,
        "description": process_desc,
        "sql_expression": sql_expr_lower,
        # "pipeline": row[PIPELINE_NAME_COL],
        # "process_name": row[PROCESS_NAME_COL],
        "masking": masking
    }


def get_pipeline_id(project_id, pipeline_name):
    return f"{project_id}/pipelines/{pipeline_name}"
# Prophecy Lineage Extractor Documentation

## Description
The `Prophecy Lineage Extractor` is a tool to extract lineage information from Prophecy projects and pipelines. It allows users to specify a project, pipeline, and branch, and outputs the extracted lineage to a specified directory. Optional features include email notifications.

---

## Usage
```bash
python -m prophecy_lineage_extractor --project-id &lt;PROJECT_ID&gt; --pipeline-id &lt;PIPELINE_ID&gt; --output-dir &lt;OUTPUT_DIRECTORY&gt; [--send-email] [--branch &lt;BRANCH_NAME&gt;] [--recursive_extract &lt;true/false&gt;] [--run_for_all &lt;true/false&gt;]

```
* We must need to set these env variables **PROPHECY_URL** and **PROPHECY_PAT**
---
## Arguments
### Required Arguments
* **--project-id**
  * Type: str
  * Description: Prophecy Project ID.
  * Required: Yes

*  **--pipeline-id** 
    * Type: str
    * Description: Prophecy Pipeline ID.
    * Required: Yes
* **--output-dir**
  * Type: str
  * Description: Output directory inside the project where lineage files will be stored.
  * Required: Yes

### Optional Arguments
* --run_for_all
  * Type: boolean flag
  * Description: If Specified, a Project level Lineage Excel file is created as an Overall Project.
* --recursive-extract
  * Type: boolean flag
  * Description: If Specified, for any column from a source, which has been changed upstream, a recursive search for the same is displayed. 
* --send-email
  * Type: flag
  * Description: If specified, sends an email with the generated lineage report to ENV variable **RECEIVER_EMAIL**.
  * We must set following Env variables for this option if passed
    * SMTP_HOST
    * SMTP_PORT
    * SMTP_USERNAME
    * SMTP_PASSWORD
    * RECEIVER_EMAIL
    
* --branch
  * Type: str
  * Description: Branch to run the lineage extractor on.
  * Default: default branch in Prophecy, generally 'main or master'

---
## Running

* Please run extractor as following, it needs env variables
* we Only need to set SMTP creds if we plan to pass `--send-email` argument

```shell
export PROPHECY_URL=https://app.prophecy.io
export PROPHECY_PAT=${{ secrets.PROPHECY_PAT }}

# These are needed if you using --send-email option
export SMTP_HOST=smtp.gmail.com
export SMTP_PORT=587
export SMTP_USERNAME=${{ secrets.SMTP_USERNAME }}
export SMTP_PASSWORD=${{ secrets.SMTP_PASSWORD }}
export RECEIVER_EMAIL=ashish@prophecy.io

python -m prophecy_lineage_extractor --project-id 36587 --pipeline-id 36587/pipelines/customer_orders_demo --send-email --branch dev
```

---
## Github Action Guide

* This extactor can be setup in Github Action of a Prophecy project to get email of lineage on every commit to main
* Following is a sample of github action we can use on default branch
[Github Action default branch](https://github.com/pateash/ProphecyHelloWorld/blob/main/.github/workflows/prophecy_lineage_extractor.yml)

* Following is a sample of github action we can use on custom branch
[Github Action custom branch](https://github.com/pateash/ProphecyHelloWorld/blob/main/.github/workflows/prophecy_lineage_extractor_dev.yml)


---
## Gitlab Action Guide
* Following is a sample of gitlab action we can use on a branch
[Gitlab Action guide](https://github.com/pateash/ProphecyHelloWorld/blob/main/.gitlab-ci.yml)
* Note—we need to create gitlab CI/CD variables(secrets) for using them in our YML file, ex. SMTP_USER etc.
* additionally, we will also need to setup an ACCESS_TOKEN to allow the JOB to commit if commit is enabled.

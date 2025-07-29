from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from pytz import timezone
from databricks.sdk import WorkspaceClient
from pyspark.sql import SparkSession
import sys
import time
import json
import os
import logging
import pandas as pd
from .utils import (
    execute_run_databricks,
    execute_run_postgres,
    DbConnections
)

class RuleManager:
    def __init__(self, base_dir: Optional[str] = None):
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)
        self.config: Dict[str, Any] = {}
        self.template: Dict[str, Any] = {}
        self.rules: Dict[str, List[Dict[str, Any]]] = {}
        self.execution_id: Optional[int] = None
        self.job_start_time: Optional[float] = None
        self.databricks_client = WorkspaceClient()

        if base_dir:
            self.base_dir = base_dir
        else:
            self.base_dir = os.path.dirname(os.path.abspath(__file__))

    def load_config(self, config_path: str):
        with open(config_path, 'r') as f:
            self.config = json.load(f)

    def split_config_object(self):
        if 'RULES' in self.config:
            self.template = {k: v for k, v in self.config.items() if k != 'RULES'}
            self.rules = {'RULES': self.config['RULES']}
            return self.template, self.rules
        else:
            self.logger.warning("Array 'RULES' not found in rule object.")
            return self.template, None

    def run_exe(self, s: str) -> int:
        # Use consistent hashing and ensure non-negative number
        return abs(hash(s)) % (sys.maxsize + 1)

    def init_other_variables(self):
        # Use UTC date to avoid timezone issues
        hash_string = (datetime.utcnow() - timedelta(days=1)).strftime("%Y%m%d%H%M%S")
        self.execution_id = self.run_exe(hash_string)
        self.job_start_time = time.time()

    def set_system_variables(self, rule: Dict[str, Any]) -> Dict[str, Any]:
        self.init_other_variables()
        hash_string = f"{rule['TEAM_NAME']}{rule['DOMAIN_NAME']}{rule['RULE_CATEGORY_NAME']}{rule['RULE_ID']}"
        unique_rule_identifier = self.run_exe(hash_string)
        rule['EXECUTION_ID'] = self.execution_id
        rule['UNIQUE_RULE_IDENTIFIER'] = unique_rule_identifier
        rule['UNIQUE_TIMESTAMP'] = datetime.utcnow().strftime("%Y%m%d%H%M%S%f")
        return rule

    def get_file_text(self, file_path: str, is_local: bool = False) -> str:
        """Read file content from local filesystem or Databricks workspace.
        
        Args:
            file_path: Path to the file
            is_local: Whether the file is local or in Databricks workspace
            
        Returns:
            str: File contents
            
        Raises:
            FileNotFoundError: If local file not found
            Exception: For other errors
        """
        if is_local:
            try:
                # First, try to find SQL templates in the package directory
                package_dir = os.path.dirname(os.path.abspath(__file__))
                possible_paths = [
                    os.path.join(package_dir, 'sql_templates', file_path),  # Package sql_templates
                    os.path.join(os.getcwd(), 'sql_templates', file_path),  # Current directory sql_templates
                    os.path.join(self.base_dir, 'sql_templates', file_path),  # Base directory sql_templates
                ]

                # Add user-specified templates path if available
                if hasattr(self, 'sql_templates_path'):
                    possible_paths.insert(0, os.path.join(self.sql_templates_path, file_path))

                for path in possible_paths:
                    if os.path.exists(path):
                        full_path = path
                        break
                else:
                    raise FileNotFoundError(f"SQL template not found: {file_path}")

                self.logger.info(f"Reading local file: {full_path}")
                with open(full_path, 'r') as file:
                    return file.read()

            except Exception as e:
                self.logger.error(f"Error reading file {file_path}: {str(e)}")
                raise
        else:
            # Download file content from Databricks workspace
            try:
                with self.databricks_client.workspace.download(file_path) as f:
                    return f.read().decode("utf-8")
            except Exception as e:
                self.logger.error(f"Error downloading from Databricks: {str(e)}")
                raise

    def set_dynamic_context_values(self, rule: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process RULE_DYNAMIC_CONTEXT to load dynamic key-value pairs from SQL file.
        
        Args:
            rule: Rule configuration dictionary
            
        Returns:
            Updated rule with dynamic context values
        """
        dynamic_context_path = rule.get('RULE_DYNAMIC_CONTEXT')
        
        if not dynamic_context_path:
            print("DEBUG: No RULE_DYNAMIC_CONTEXT found in rule")
            self.logger.debug("No RULE_DYNAMIC_CONTEXT found in rule, skipping dynamic context processing")
            return rule
            
        try:
            print(f"DEBUG: Found RULE_DYNAMIC_CONTEXT: {dynamic_context_path}")
            self.logger.info(f"Processing dynamic context from: {dynamic_context_path}")
            
            # Remove leading slash if present and normalize path
            if dynamic_context_path.startswith('/'):
                dynamic_context_path = dynamic_context_path[1:]
            
            print(f"DEBUG: Normalized path: {dynamic_context_path}")
            
            # Get SQL content from the context file
            context_sql = self.get_file_text(dynamic_context_path, is_local=True)
            context_sql = context_sql.replace(';', '').strip()
            
            print(f"DEBUG: Context SQL loaded: {context_sql[:100]}...")  # First 100 chars
            self.logger.info(f"Executing dynamic context SQL: {context_sql}")
            
            # Execute SQL based on engine type
            engine_type = rule.get('ENGINE_TYPE', '').lower()
            print(f"DEBUG: Engine type: {engine_type}")
            
            if engine_type == 'databricks':
                result = execute_run_databricks(context_sql, True)
            elif engine_type == 'postgres':
                db_connection = DbConnections()
                engine = db_connection.postgres_engine()
                result = execute_run_postgres(context_sql, engine, True)
            else:
                raise ValueError(f"Unsupported ENGINE_TYPE in rule: '{engine_type}'")
            
            print(f"DEBUG: SQL execution result: {result}")
            
            # Convert result to DataFrame for easier processing
            context_df = self.get_dataframe(result)
            print(f"DEBUG: DataFrame shape: {context_df.shape}")
            print(f"DEBUG: DataFrame columns: {list(context_df.columns)}")
            print(f"DEBUG: DataFrame head:\n{context_df.head()}")
            
            if context_df.empty:
                print("DEBUG: Context DataFrame is empty!")
                self.logger.warning("Dynamic context query returned no results")
                return rule
            
            # Ensure we have the expected columns (value, key)
            if 'value' not in context_df.columns or 'key' not in context_df.columns:
                print(f"DEBUG: Missing required columns. Available: {list(context_df.columns)}")
                self.logger.error("Dynamic context query must return 'value' and 'key' columns")
                return rule
            
            # Process each row and add dynamic values to rule
            dynamic_values_added = 0
            print("DEBUG: Processing context values...")
            
            for idx, row in context_df.iterrows():
                key = str(row['key']).strip()
                value = str(row['value']).strip()
                
                print(f"DEBUG: Row {idx}: key='{key}', value='{value}'")
                
                if key and value:
                    # Add the key-value pair to the rule
                    rule[key] = value
                    dynamic_values_added += 1
                    print(f"DEBUG: Successfully added: {key} = {value}")
                    self.logger.info(f"Added dynamic context: {key} = {value}")
            
            print(f"DEBUG: Total dynamic values added: {dynamic_values_added}")
            self.logger.info(f"Successfully added {dynamic_values_added} dynamic context values to rule")
            
                        
        except FileNotFoundError as e:
            print(f"DEBUG: File not found error: {str(e)}")
            self.logger.error(f"Dynamic context file not found: {dynamic_context_path}. Error: {str(e)}")
        except Exception as e:
            print(f"DEBUG: General error: {str(e)}")
            self.logger.error(f"Error processing dynamic context: {str(e)}")
            # Don't raise the exception to allow rule processing to continue
        
        return rule


    def set_business_rule_check_templates(self, rule: Dict[str, Any]) -> Dict[str, Any]:
        """Load SQL templates based on engine type.
        
        Args:
            rule: Rule configuration dictionary
            
        Returns:
            Updated rule with SQL templates
        """
        engine_type = rule.get('ENGINE_TYPE', '').lower()
        
        # First try package sql_templates directory
        package_dir = os.path.dirname(os.path.abspath(__file__))
        template_dir = os.path.join(package_dir, 'sql_templates')
        
        if engine_type == 'databricks':
            paths = {
                'bookmark_sql_text': os.path.join('common', 'bookmark_select.sql'),
                'result_sql_txt': os.path.join('business_rule_check', 'result.sql'),
                'update_bookmark_sql_text': os.path.join('common', 'bookmark_update.sql'),
                'unique_rule_mapping_sql': os.path.join('common', 'unique_rule_mapping.sql'),
            }
        elif engine_type == 'postgres':
            paths = {
                'bookmark_sql_text': os.path.join('common', 'bookmark_select_postgres.sql'),
                'result_sql_txt': os.path.join('business_rule_check', 'result_postgres.sql'),
                'update_bookmark_sql_text': os.path.join('common', 'bookmark_update_postgres.sql'),
                'unique_rule_mapping_sql': os.path.join('common', 'unique_rule_mapping_postgres.sql'),
            }
        else:
            raise ValueError(f"Unsupported ENGINE_TYPE in rule: '{engine_type}'")

        for key, path in paths.items():
            rule[key] = self.get_file_text(path, is_local=True)

        return rule

    def set_bookmark_value(self, rule: Dict[str, Any]) -> Dict[str, Any]:
        try:
            rule['BOOKMARK_COLUMN'] = rule.get('BOOKMARK_COLUMN', 'TEMP_COL_FOR_BOOKMARK')
            rule['BOOKMARK_START_DATE'] = rule.get('DEFAULT_BOOKMARK_START_DATE', '1970-01-01')
            self.logger.info(f"Default bookmark start date: {rule['BOOKMARK_START_DATE']}")

            if rule['BOOKMARK_COLUMN'] == 'TEMP_COL_FOR_BOOKMARK':
                return self._handle_temp_bookmark(rule)

            return self._handle_actual_bookmark(rule)

        except Exception as e:
            self.logger.error(f"Error setting bookmark value: {str(e)}")
            raise

    def _handle_temp_bookmark(self, rule: Dict[str, Any]) -> Dict[str, Any]:
        rule.update({
            'SKIP_BOOKMARKING': True,
            'NEED_BOOKMARK_UPDATE': False,
            'BOOKMARK_END_DATE': '2099-01-01'
        })
        return rule

    def _handle_actual_bookmark(self, rule: Dict[str, Any]) -> Dict[str, Any]:
        rule.update({
            'SKIP_BOOKMARKING': False,
            'NEED_BOOKMARK_UPDATE': True,
            'BOOKMARK_END_DATE': rule.get('BOOKMARK_END_DATE', rule['BOOKMARK_START_DATE'])
        })

        if 'bookmark_sql_text' not in rule:
            return rule

        return self._process_bookmark_sql(rule)

    def _process_bookmark_sql(self, rule: Dict[str, Any]) -> Dict[str, Any]:
        rule['bookmark_sql_text'] = self.replace_common_variables(rule['bookmark_sql_text'], rule)
        engine_type = rule.get('ENGINE_TYPE', '').lower()

        if engine_type == 'databricks':
            result = execute_run_databricks(rule['bookmark_sql_text'], True)
        elif engine_type == 'postgres':
            db_connection = DbConnections()
            engine = db_connection.postgres_engine()
            result = execute_run_postgres(rule['bookmark_sql_text'], engine, True)
        else:
            raise ValueError(f"Unsupported ENGINE_TYPE in rule: '{engine_type}'")

        # Expecting result to be list with at least two elements (date range)
        if isinstance(result, list) and len(result) > 1 and len(result[1]) > 1:
            rule['BOOKMARK_START_DATE'] = result[1][0]
            rule['BOOKMARK_END_DATE'] = result[1][1]
            if rule['BOOKMARK_END_DATE'] < rule['BOOKMARK_START_DATE']:
                rule['BOOKMARK_END_DATE'] = rule['BOOKMARK_START_DATE']
        else:
            rule['BOOKMARK_END_DATE'] = (datetime.now(timezone('UTC')) - timedelta(days=1)).date().isoformat()

        return rule

    def get_dataframe(self, result: Any) -> pd.DataFrame:
        df = pd.DataFrame()
        if result:
            result_df = pd.DataFrame(result)
            if len(result_df) > 0:
                df_header = result_df.iloc[0]
                result_df = result_df[1:]
                result_df.columns = df_header
                df = result_df.reset_index(drop=True)
        return df

    def process_fail_sql(self, rule: Dict[str, Any]) -> Dict[str, Any]:
        fail_sql_path = rule.get('FAIL_SQL')
        
        if not fail_sql_path:
            rule['STATUS'] = True
            rule['FAIL_RECORD_COUNT'] = 0
            rule['FAILED_KEYS'] = ''
            return rule

        rule['STATUS'] = False
        rule['STOP_ON_FAIL_STATUS'] = rule.get('STOP_ON_FAIL_STATUS').upper() == 'TRUE' 
        fail_sql_path = os.path.normpath(os.path.join(self.base_dir, fail_sql_path))
        self.logger.info(f"Reading fail SQL file from: {fail_sql_path}")

        try:
            rule['FAILED_QUERY'] = self.get_file_text(str(fail_sql_path), is_local=True).replace(';', '')
        except Exception as e:
            self.logger.error(f"Error reading fail SQL file: {e}")
            rule['FAILED_QUERY'] = ''
            rule['FAIL_RECORD_COUNT'] = 0
            rule['FAILED_KEYS'] = ''
            return rule

        pass_sql_path = rule.get('PASS_SQL', '')
        if pass_sql_path:
            pass_sql_path = os.path.normpath(os.path.join(self.base_dir, pass_sql_path))
            try:
                rule['PASS_QUERY'] = self.get_file_text(str(pass_sql_path), is_local=True).replace(';', '')
            except Exception as e:
                self.logger.error(f"Error reading pass SQL file: {e}")
                rule['PASS_QUERY'] = ''
        else:
            rule['PASS_QUERY'] = ''

        rule['FAILED_QUERY'] = self.replace_common_variables(rule['FAILED_QUERY'], rule)

        engine_type = rule.get('ENGINE_TYPE', '').lower()
        if engine_type == 'databricks':
            fail_df_result = execute_run_databricks(rule['FAILED_QUERY'], True)
        elif engine_type == 'postgres':
            db_connection = DbConnections()
            engine = db_connection.postgres_engine()
            fail_df_result = execute_run_postgres(rule['FAILED_QUERY'], engine, True)
        else:
            raise ValueError(f"Unsupported ENGINE_TYPE in rule: '{engine_type}'")

        fail_df = self.get_dataframe(fail_df_result)
        fail_df_count = fail_df.shape[0]
        rule['FAIL_RECORD_COUNT'] = fail_df_count

        if rule['FAIL_RECORD_COUNT'] == 0 and rule['PASS_QUERY'] == '':
            rule['STATUS'] = True

        try:
            fail_df_keys = fail_df.head(10).to_json(orient="records")
            fail_df_keys_parsed = json.loads(fail_df_keys)
            rule['FAILED_KEYS'] = json.dumps(fail_df_keys_parsed, indent=4)
        except Exception as e:
            self.logger.error(f"Error converting failed keys to JSON: {e}")
            rule['FAILED_KEYS'] = '{}'

        return rule
    
    def process_pass_sql(self, rule: Dict[str, Any]) -> Dict[str, Any]:
        if rule['PASS_QUERY'] != '':
            engine_type = rule.get('ENGINE_TYPE', '').lower()
            if engine_type == 'databricks':
                pass_df_result = execute_run_databricks(rule['PASS_QUERY'], True)
            else:
                db_connection = DbConnections()
                engine = db_connection.postgres_engine()
                pass_df_result = execute_run_postgres(rule['PASS_QUERY'], engine, True)
                
            pass_df = self.get_dataframe(pass_df_result)
            pass_df_count = pass_df.shape[0]
            rule['PASS_RECORD_COUNT'] = pass_df_count
                
            if (rule['PASS_RECORD_COUNT'] + rule['FAIL_RECORD_COUNT']) == 0:
                rule['PASS_PERCENTAGE'] = 0
            else:
                rule['PASS_PERCENTAGE'] = round(
                    (rule['PASS_RECORD_COUNT'] / (rule['PASS_RECORD_COUNT'] + rule['FAIL_RECORD_COUNT'])) * 100, 2
                )
                
            if int(rule['PASS_PERCENTAGE']) >= int(rule['PASS_THRESHOLD']):
                rule['STATUS'] = True
                rule['REMARKS'] = 'Percentage of records passed test is {}. Threshold: {}.'.format(
                    rule['PASS_PERCENTAGE'], rule['PASS_THRESHOLD']
                )
            elif rule['PASS_PERCENTAGE'] == 0:
                rule['REMARKS'] = 'Both passed records count and failed records count are zero'
            else:
                rule['REMARKS'] = 'Percentage of records passed test is {}. Threshold: {}. Some failed keys are: {}'.format(
                    rule['PASS_PERCENTAGE'], rule['PASS_THRESHOLD'], rule['FAILED_KEYS']
                )
        elif not rule['STATUS']:
            rule['PASS_PERCENTAGE'] = 100
            rule['PASS_RECORD_COUNT'] = 0
            rule['REMARKS'] = '{} number of records failed the test. Some failed keys are: {}'.format(
                rule['FAIL_RECORD_COUNT'], rule['FAILED_KEYS']
            )
        else:
            rule['PASS_PERCENTAGE'] = 100
            rule['PASS_RECORD_COUNT'] = 0
            rule['REMARKS'] = 'No record has failed the test'
        
        return rule

    def replace_common_variables(self,sql_str, rule):
        """
        Replaces placeholders in sql_str with corresponding values from the rule dictionary.
        Any placeholder in the format <PLACEHOLDER_NAME> will be dynamically replaced.
        """
        final_sql = sql_str
        for key, value in rule.items():
            placeholder = f'<{key}>'
            final_sql = final_sql.replace(placeholder, str(value))
        return final_sql


    def set_business_rule_check_final_queries(self, rule: dict) -> dict:
        rule['unique_rule_mapping_sql'] = self.replace_common_variables(rule.get('unique_rule_mapping_sql', ''), rule)
        rule['result_sql_txt'] = self.replace_common_variables(rule.get('result_sql_txt', ''), rule)
        rule['update_bookmark_sql_text'] = self.replace_common_variables(rule.get('update_bookmark_sql_text', ''), rule)
        return rule

   
    def exec_business_rule_check_final_queries(self, rule):
        """Execute final SQL queries based on engine type (databricks or postgres)."""
        print("Executing final queries")
        engine_type = rule.get("ENGINE_TYPE").lower()
        print("exec_business_rule_check_final_queries", engine_type)
        
        try:
            def clean_sql(sql):
                if not sql:
                    return ""
                # Remove trailing semicolons, quotes, commas and normalize whitespace
                cleaned = sql.strip().rstrip(';').rstrip("'").rstrip(",").strip()
                return cleaned

            # Clean all SQL queries
            rule["unique_rule_mapping_sql"] = clean_sql(rule.get("unique_rule_mapping_sql", ""))
            rule["result_sql_txt"] = clean_sql(rule.get("result_sql_txt", ""))
            rule["update_bookmark_sql_text"] = clean_sql(rule.get("update_bookmark_sql_text", ""))

            if engine_type == 'databricks':
                print("Running Databricks...")
                execute_run_databricks(rule["unique_rule_mapping_sql"], False)
                execute_run_databricks(rule["result_sql_txt"], False)
                if rule.get('NEED_BOOKMARK_UPDATE', False):
                    execute_run_databricks(rule["update_bookmark_sql_text"], False)

            else:  # Assume Postgres
                print("Running Postgres...")
                db_connection = DbConnections()
                engine = db_connection.postgres_engine()

                try:
                    execute_run_postgres(rule["unique_rule_mapping_sql"], engine, False)
                except Exception as e:
                    print(f"Error executing unique_rule_mapping_sql: {str(e)}")

                try:
                    execute_run_postgres(rule["result_sql_txt"], engine, False)
                except Exception as e:
                    print(f"Error executing result_sql_txt: {str(e)}")

                if rule.get('NEED_BOOKMARK_UPDATE', False):
                    try:
                        execute_run_postgres(rule["update_bookmark_sql_text"], engine, False)
                    except Exception as e:
                        print(f"Error executing update_bookmark_sql_text: {str(e)}")

        except Exception as e:
            print(f"Error executing final queries: {str(e)}")
            raise

        return rule


    def business_rule_check(self) -> Dict[str, List[Dict[str, Any]]]:
        if self.template.get("RULE_CATEGORY_NAME") == 'BUSINESS_RULE_CHECK':
            for idx, rule in enumerate(self.rules.get("RULES", [])):
                
                rule = {**self.template, **rule}
                rule = self.set_system_variables(rule)
                rule = self.set_dynamic_context_values(rule)
                rule = self.set_business_rule_check_templates(rule)
                rule = self.set_bookmark_value(rule)
                rule = self.process_fail_sql(rule)
                rule = self.process_pass_sql(rule)
                rule = self.set_business_rule_check_final_queries(rule)
                
                
                rule = self.exec_business_rule_check_final_queries(rule)


                self.rules["RULES"][idx] = rule  
                self.logger.info(json.dumps(rule, indent=2))

                rule_name = rule.get('RULE_NAME', 'Unknown')
                rule_id = rule.get('RULE_ID', 'Unknown')
                
                
                if rule.get('STOP_ON_FAIL_STATUS'): # for checking as per user input
                    self.logger.warning(f"Rule {rule_name} (ID: {rule_id}) failed with STOP_ON_FAIL_STATUS=TRUE. Stopping execution of remaining rules.")
                     
                    if not rule.get('STATUS'): # for checking as per rule status
                        self.logger.warning(f"Rule {rule_name} (ID: {rule_id}) failed STATUS is FALSE.")         
                        break
                
            return self.rules



from pathlib import Path

ARG_KEYWORD_IMPORTS = "imports"
ARG_KEYWORD_LOOP = "loop"
ARG_KEYWORD_META = "meta"
ARG_KEYWORD_ARGUMENTS = "arguments"
ARG_KEYWORD_PIPELINE_EXT = "pipeline_extension"

DEFAULT_IO_DATA_LABEL = ""
INPUT_PATH = "input_path"
OUTPUT_PATH = "output_path"
TMP_PATHS = "tmp_paths"
TMP_PATH_INDEX = "tmp_path_index"
DB_CONFIG = "database_configs"

PROJECT_PATH = Path(__file__).parents[1]
CSV_NAME_PATH = PROJECT_PATH / "mcp_use_case_testing_duckdb" / "testing_csv.csv"

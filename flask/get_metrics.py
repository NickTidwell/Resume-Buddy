from helpers.metrics import get_stat_average,get_llm_score
jsonl_file = "outputs/output.jsonl"

get_stat_average(jsonl_file)
get_llm_score(jsonl_file)
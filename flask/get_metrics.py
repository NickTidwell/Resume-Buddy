from helpers.metrics import get_stat_average,get_llm_score

base_path = "outputs"
files = [
"physical_output.jsonl",
"nurse_output.jsonl",
"finance_output.jsonl",
"software_output.jsonl",
"graphic_output.jsonl",
"teacher_output.jsonl",
]
for file in files:
    jsonl_file = f"{base_path}/{file}"
    print(f"===== Score for {jsonl_file} =====") 
    get_stat_average(jsonl_file)
    get_llm_score(jsonl_file)
    print("====================================\n\n")
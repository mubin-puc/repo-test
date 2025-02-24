import redis
import csv
from collections import defaultdict

# Connect to Redis
redis_client = redis.StrictRedis(host='localhost', port=6379, decode_responses=True)

# File paths
run_file = "/home/nitindevella/Downloads/terraform_run_2025-01-30.csv"
resource_file = "/home/nitindevella/Downloads/terraform_run_resources_2025-01-30.csv"

# Dictionary to hold merged data
merged_data = defaultdict(dict)

# Function to load CSV and merge by run_id
def load_csv(file_path, key_field):
    with open(file_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            run_id = row.get(key_field)
            if run_id:
                merged_data[run_id].update(row)

# Load both CSVs (correcting field names)
load_csv(run_file, "run_id")
load_csv(resource_file, "run_id")

# Store merged data in Redis Hashes
for run_id, data in merged_data.items():
    redis_client.hset(f"run:{run_id}", mapping=data)

print("✅ Data successfully stored in Redis Hashes.")

# Function to create RediSearch index
def create_redisearch_index():
    try:
        redis_client.execute_command("FT.DROPINDEX idx_runs DD")
        print("ℹ️ Dropped existing index.")
    except redis.exceptions.ResponseError:
        print("ℹ️ No existing index to drop.")

    # Create the new index
    redis_client.execute_command(
        "FT.CREATE idx_runs ON HASH PREFIX 1 run: "
        "SCHEMA run_id TAG SORTABLE "
        "tfe_workspace_id TAG SORTABLE "
        "run_time NUMERIC SORTABLE"
    )
    print("✅ RediSearch index 'idx_runs' created successfully.")

# Create RediSearch index
create_redisearch_index()

https://rpmfind.net/linux/fedora/linux/development/rawhide/Everything/x86_64/os/Packages/p/python3-redis-5.2.1-1.fc43.noarch.rpm

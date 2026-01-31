from config import supabase

def check_semantic_equivalence(old, new):
    try:
        # Check if numbers are close enough
        if isinstance(old, (int, float)) and isinstance(new, (int, float)):
             return abs(float(old) - float(new)) < 0.01
        
        # Check if string representation of number is equal to number
        if isinstance(old, (int, float)) and isinstance(new, str):
            try:
                return abs(float(old) - float(new)) < 0.01
            except ValueError:
                return False
        if isinstance(old, str) and isinstance(new, (int, float)):
            try:
                return abs(float(old) - float(new)) < 0.01
            except ValueError:
                return False
                
        return False
    except:
        return False

def log_to_supabase(table, data):
    """Log data to Supabase table.
    
    For shadow_tests table, remaps 'request_id' to 'test_id' to match schema.
    Also remaps 'diff_summary' to 'diff_report'.
    """
    try:
        # Remap fields for shadow_tests table to match Supabase schema
        if table == "shadow_tests":
            mapped_data = data.copy()
            if "request_id" in mapped_data:
                mapped_data["test_id"] = mapped_data.pop("request_id")
            if "diff_summary" in mapped_data:
                mapped_data["diff_report"] = mapped_data.pop("diff_summary")
            # Add required status field
            if "status" not in mapped_data:
                mapped_data["status"] = "pending"
            # Remove fields not in schema
            for field in ["flags", "legacy_time", "headless_time", "retries_used"]:
                mapped_data.pop(field, None)
            data = mapped_data
            
        supabase.table(table).insert(data).execute()
    except Exception as e:
        print(f"Error logging to Supabase table {table}: {e}")


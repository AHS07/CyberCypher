from config import supabase

result = supabase.table('shadow_tests').select('test_id,status,error_message').order('created_at', desc=True).limit(3).execute()

print("Recent tests:")
for test in result.data:
    print(f"- {test['test_id']}: {test['status']}")
    if test.get('error_message'):
        print(f"  Error: {test['error_message']}")
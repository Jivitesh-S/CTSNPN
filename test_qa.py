from backend.rag_service import RAGService
svc = RAGService()

# Test 1: Product with full docs (P020 - Galaxy S26 Ultra)
print('=== TEST 1: P020 Galaxy S26 Ultra ===')
result = svc._retrieve('What are the features of Samsung Galaxy S26 Ultra?', shop_id='S001', product_id='P020')
print(f'Found {len(result)} results')
if result:
    print(f'Top result: Product={result[0].get("product_name")}, Shop={result[0].get("shop_name")}')
    context = svc._build_context(result)
    answer = svc._generate_answer('What are the features of Samsung Galaxy S26 Ultra?', context, history=[])
    print(f'Answer: {answer[:200]}...')

# Test 2: Product with truncated docs (P022 - Galaxy S26)
print()
print('=== TEST 2: P022 Galaxy S26 ===')
result = svc._retrieve('What are the specs of Samsung Galaxy S26?', shop_id='S001', product_id='P022')
print(f'Found {len(result)} results')
if result:
    context = svc._build_context(result)
    answer = svc._generate_answer('What are the specs of Samsung Galaxy S26?', context, history=[])
    print(f'Answer: {answer[:200]}...')

# Test 3: Missing product (P026 - Galaxy A56 5G)
print()
print('=== TEST 3: P026 Galaxy A56 5G (missing docs) ===')
result = svc._retrieve('What are the features of Samsung Galaxy A56 5G?', shop_id='S001', product_id='P026')
print(f'Found {len(result)} results')
if result:
    context = svc._build_context(result)
    answer = svc._generate_answer('What are the features of Samsung Galaxy A56 5G?', context, history=[])
    print(f'Answer: {answer[:200]}...')
else:
    print('No results found for P026')

# Test 4: Existing product (baseline)
print()
print('=== TEST 4: P001 (baseline) ===')
result = svc._retrieve('What are the features of Samsung Galaxy Buds3 Pro?', shop_id='S001', product_id='P001')
print(f'Found {len(result)} results')
if result:
    context = svc._build_context(result)
    answer = svc._generate_answer('What are the features of Samsung Galaxy Buds3 Pro?', context, history=[])
    print(f'Answer: {answer[:200]}...')

# Test 5: Accessory (A021 - Buds4 Pro)
print()
print('=== TEST 5: A021 Buds4 Pro ===')
result = svc._retrieve('What are the features of Samsung Galaxy Buds4 Pro?', shop_id='S001', product_id='A021')
print(f'Found {len(result)} results')
if result:
    context = svc._build_context(result)
    answer = svc._generate_answer('What are the features of Samsung Galaxy Buds4 Pro?', context, history=[])
    print(f'Answer: {answer[:200]}...')

# Test 6: Watch (A015 - Watch8 40mm)
print()
print('=== TEST 6: A015 Watch8 40mm ===')
result = svc._retrieve('What are the features of Samsung Galaxy Watch8 40mm?', shop_id='S001', product_id='A015')
print(f'Found {len(result)} results')
if result:
    context = svc._build_context(result)
    answer = svc._generate_answer('What are the features of Samsung Galaxy Watch8 40mm?', context, history=[])
    print(f'Answer: {answer[:200]}...')
else:
    print('No results found for A015')

# Test 7: Laptop (L015 - Book6 Pro)
print()
print('=== TEST 7: L015 Book6 Pro ===')
result = svc._retrieve('What are the specs of Samsung Galaxy Book6 Pro?', shop_id='S001', product_id='L015')
print(f'Found {len(result)} results')
if result:
    context = svc._build_context(result)
    answer = svc._generate_answer('What are the specs of Samsung Galaxy Book6 Pro?', context, history=[])
    print(f'Answer: {answer[:200]}...')
else:
    print('No results found for L015')
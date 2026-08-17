from backend.rag_service import RAGService
import time
svc = RAGService()

tests = [
    ('P020', 'Samsung Galaxy S26 Ultra', 'What are the features?'),
    ('P022', 'Samsung Galaxy S26', 'What are the specs?'),
    ('P026', 'Samsung Galaxy A56 5G', 'What are the features?'),
    ('A021', 'Samsung Galaxy Buds4 Pro', 'What are the features?'),
    ('A015', 'Samsung Galaxy Watch8 40mm', 'What are the features?'),
    ('L015', 'Samsung Galaxy Book6 Pro', 'What are the specs?'),
    ('P001', 'Samsung Galaxy Buds3 Pro', 'What are the features?'),  # baseline
]

for product_id, name, question in tests:
    print(f'\n=== {name} (ID: {product_id}) ===')
    start = time.time()
    result = svc._retrieve(question, shop_id='S001', product_id=product_id)
    elapsed = time.time() - start
    print(f'Retrieval: {len(result)} results in {elapsed:.2f}s')
    if result:
        # Just show first result's product name and similarity
        r = result[0]
        print(f'  Top: id={r.get("id")}, product_name={r.get("product_name")}, similarity={r.get("similarity"):.3f}')
    else:
        print('  No results found')
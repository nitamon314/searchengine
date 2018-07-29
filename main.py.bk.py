

number_doc = 3

def init_document():
    for i in range(number_doc - 1):
        doc_text = 



#initialize all vects
init_document()

generate_inverted_index()

#apply tf-idf for some values
apply_tf-idf()

query = raw_input("Enter query")
if len(query) <= 0:
    break
filtered_query_list = get_filtered_list(query)
query_vector = genarate_vector(filtered_query_list)
get_tf_idf_from_query_vector(query_vector)
results = get_search_results(query_vector)

for tup in results:
    print("Document id : " + str(tup[0].zfill(4) + " Weight : " + str(tup[1])))
    
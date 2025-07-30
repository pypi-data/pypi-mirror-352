from lollms_client import LollmsClient, MSG_TYPE
from ascii_colors import ASCIIColors, trace_exception
from typing import List, Dict, Any, Optional, Callable
import json
from pathlib import Path

# --- Dependency Management for the Search Tool ---
# Ensure the duckduckgo_search library is installed for our RAG query function.
try:
    import pipmaster as pm
    pm.ensure_packages(["duckduckgo_search"])
    from duckduckgo_search import DDGS
    _ddgs_installed = True
except Exception as e_dep:
    _ddgs_installed = False
    ASCIIColors.error(f"Could not ensure/import duckduckgo_search: {e_dep}")
    ASCIIColors.warning("The RAG function in this example will not work.")
    DDGS = None
# --- End Dependency Management ---


def internet_rag_query_function(
    query_text: str,
    vectorizer_name: Optional[str] = None, # Not used for this keyword-based search
    top_k: int = 5,
    min_similarity_percent: float = 0.0 # Not used for this keyword-based search
) -> List[Dict[str, Any]]:
    """
    A RAG-compatible query function that performs a live internet search using DuckDuckGo.

    Args:
        query_text: The search query.
        vectorizer_name: Ignored by this function.
        top_k: The maximum number of search results to return.
        min_similarity_percent: Ignored by this function.

    Returns:
        A list of dictionaries, each formatted for RAG with 'document', 'content', and 'similarity'.
    """
    if not _ddgs_installed:
        ASCIIColors.error("duckduckgo_search library is not available. Cannot perform internet search.")
        return []

    ASCIIColors.magenta(f"  [INTERNET RAG] Searching web for: '{query_text}', max_results={top_k}")
    formatted_results = []
    try:
        with DDGS() as ddgs:
            # Fetch search results from DuckDuckGo
            search_results = ddgs.text(keywords=query_text, max_results=top_k)
            
            if not search_results:
                ASCIIColors.yellow("  [INTERNET RAG] DuckDuckGo returned no results for this query.")
                return []

            for i, result in enumerate(search_results):
                # Format the search result into the structure expected by generate_text_with_rag
                # 'document' will be the URL.
                # 'content' will be a combination of title and snippet.
                # 'similarity' is emulated based on rank, as DDG doesn't provide a score.
                formatted_results.append({
                    "document": result.get("href", "#"),
                    "similarity": round(100.0 - (i * (10.0 / top_k)), 2), # Create a descending score
                    "content": f"Title: {result.get('title', 'N/A')}\nSnippet: {result.get('body', 'N/A')}"
                })
        
        ASCIIColors.magenta(f"  [INTERNET RAG] Found {len(formatted_results)} results.")
        return formatted_results

    except Exception as e:
        trace_exception(e)
        ASCIIColors.error(f"  [INTERNET RAG] An error occurred during search: {e}")
        return []

# --- Streaming Callback for RAG and LLM ---
# (This is the same useful callback from the previous example)
def rag_streaming_callback(
    chunk: str, 
    msg_type: MSG_TYPE, 
    metadata: Optional[Dict] = None, 
    turn_history: Optional[List] = None
) -> bool:
    metadata = metadata or {}
    hop = metadata.get("hop", "")
    type_info = metadata.get("type", "N/A")

    if msg_type == MSG_TYPE.MSG_TYPE_CHUNK:
        ASCIIColors.success(chunk, end="", flush=True)
    elif msg_type == MSG_TYPE.MSG_TYPE_STEP_START:
        info = metadata.get("query", chunk) if type_info in ["rag_query_generation", "rag_retrieval"] else chunk
        ASCIIColors.yellow(f"\n>> RAG Hop {hop} | START | {type_info.upper()} | Info: {str(info)[:100]}...", flush=True)
    elif msg_type == MSG_TYPE.MSG_TYPE_STEP_END:
        num_chunks = metadata.get("num_chunks")
        query = metadata.get("query")
        decision = metadata.get("decision")
        
        end_info = []
        if query: end_info.append(f"Query: '{str(query)[:50]}...'")
        if num_chunks is not None: end_info.append(f"Retrieved: {num_chunks} sources")
        if decision: end_info.append(f"LLM Decision: NeedMore={decision.get('need_more_data')}, Summary: '{str(decision.get('new_information_summary'))[:40]}...'")
        
        ASCIIColors.green(f"\n<< RAG Hop {hop} | END   | {type_info.upper()} | {' | '.join(end_info) if end_info else chunk}", flush=True)
    elif msg_type == MSG_TYPE.MSG_TYPE_EXCEPTION:
        ASCIIColors.error(f"\nError in RAG stream: {chunk}", flush=True)
    
    return True

# --- Main Example ---
if __name__ == "__main__":
    ASCIIColors.red("--- Internet Search with Multi-Hop RAG Example ---")

    LLM_BINDING_NAME = "ollama"
    LLM_MODEL_NAME = "mistral-nemo:latest" # Nemo is good with JSON and reasoning

    if not _ddgs_installed:
        ASCIIColors.error("Cannot run this example because the 'duckduckgo-search' library is not installed.")
        exit(1)

    try:
        lc = LollmsClient(
            binding_name=LLM_BINDING_NAME,
            model_name=LLM_MODEL_NAME,
            temperature=0.1,
            ctx_size=4096
        )
        ASCIIColors.green(f"LollmsClient initialized with LLM: {LLM_BINDING_NAME}/{LLM_MODEL_NAME}")

        # --- Test Case 1: Classic RAG with Internet Search ---
        ASCIIColors.cyan("\n\n--- Test Case 1: Classic RAG (max_rag_hops = 0) using Internet Search ---")
        classic_rag_prompt = "What is the James Webb Space Telescope and what was its launch date?"
        ASCIIColors.blue(f"User Prompt: {classic_rag_prompt}")

        classic_rag_result = lc.generate_text_with_rag(
            prompt=classic_rag_prompt,
            rag_query_function=internet_rag_query_function,
            max_rag_hops=0,
            rag_top_k=3,
            streaming_callback=rag_streaming_callback,
            n_predict=300
        )
        print("\n--- End of Classic RAG ---")
        ASCIIColors.magenta("\nClassic RAG Final Output Details:")
        print(f"  Final Answer (first 150 chars): {classic_rag_result.get('final_answer', '')[:150]}...")
        print(f"  Error: {classic_rag_result.get('error')}")
        print(f"  Total Unique Sources Retrieved: {len(classic_rag_result.get('all_retrieved_sources', []))}")
        if classic_rag_result.get('all_retrieved_sources'):
            print("  Retrieved Sources (URLs):")
            for source in classic_rag_result['all_retrieved_sources']:
                print(f"    - {source.get('document')}")

        # --- Test Case 2: Multi-Hop RAG with Internet Search ---
        ASCIIColors.cyan("\n\n--- Test Case 2: Multi-Hop RAG (max_rag_hops = 2) using Internet Search ---")
        multihop_prompt = "First, find out what the TRAPPIST-1 system is. Then, search for recent news about its planets from the James Webb Space Telescope."
        ASCIIColors.blue(f"User Prompt: {multihop_prompt}")
        
        multihop_rag_result = lc.generate_text_with_rag(
            prompt=multihop_prompt,
            rag_query_function=internet_rag_query_function,
            rag_query_text=None, # Let the LLM generate the first query
            max_rag_hops=2, # Allow up to two separate search queries
            rag_top_k=2,
            streaming_callback=rag_streaming_callback,
            n_predict=400,
        )
        print("\n--- End of Multi-Hop RAG ---")
        ASCIIColors.magenta("\nMulti-Hop RAG Final Output Details:")
        print(f"  Final Answer (first 150 chars): {multihop_rag_result.get('final_answer', '')[:150]}...")
        print(f"  Error: {multihop_rag_result.get('error')}")
        print(f"  Number of Hops Made: {len(multihop_rag_result.get('rag_hops_history', []))}")
        for i, hop_info in enumerate(multihop_rag_result.get('rag_hops_history', [])):
            print(f"    Hop {i+1} Query: '{hop_info.get('query')}'")
            print(f"    Hop {i+1} Retrieved Count: {len(hop_info.get('retrieved_chunks_details',[]))}")
            print(f"    Hop {i+1} LLM Decision: NeedMoreData={hop_info.get('llm_decision_json',{}).get('need_more_data')}")
        print(f"  Total Unique Sources Retrieved: {len(multihop_rag_result.get('all_retrieved_sources', []))}")
        if multihop_rag_result.get('all_retrieved_sources'):
            print("  All Retrieved Sources (URLs):")
            for source in multihop_rag_result['all_retrieved_sources']:
                print(f"    - {source.get('document')}")


    except ValueError as ve:
        ASCIIColors.error(f"Initialization or RAG parameter error: {ve}")
        trace_exception(ve)
    except ConnectionRefusedError:
        ASCIIColors.error(f"Connection refused. Is the Ollama server ({LLM_BINDING_NAME}) running?")
    except Exception as e:
        ASCIIColors.error(f"An unexpected error occurred: {e}")
        trace_exception(e)

    ASCIIColors.red("\n--- Internet Search RAG Example Finished ---")
import time
from Functions.process_single_question_wrapper import *
from asyncio import to_thread
from concurrent.futures import ProcessPoolExecutor
import multiprocessing
import concurrent.futures

async def process_multiple_questions(questions_dict, user_id, headers, openai_model):
    """
    Process multiple questions using ThreadPoolExecutor instead of asyncio.gather
    """
    total_start = time.perf_counter()
    print(f"\n=== Starting parallel processing of {len(questions_dict)} questions ===")
    
    # Configure max workers (limit concurrent processing)
    
    
    # Create futures list to store results
    results = []
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Submit all tasks
        future_to_question = {
            executor.submit(
                process_single_question_wrapper,
                question_data=question,
                key_id=key if idx == 0 else None,
                user_id=user_id,
                headers=headers,
                openai_model=openai_model,
                is_single_question=False,
                is_first_question=(idx == 0)
            ): idx 
            for idx, (key, question) in enumerate(questions_dict.items())
        }

        # Process completed futures as they finish
        for future in concurrent.futures.as_completed(future_to_question):
            idx = future_to_question[future]
            try:
                result = future.result()
                print(f"Question {idx + 1} completed successfully")
                results.append(result)
            except Exception as e:
                print(f"Question {idx + 1} generated an exception: {str(e)}")
                results.append({
                    "error": str(e),
                    "question_idx": idx
                })

    total_end = time.perf_counter()
    print(f"\nTotal execution time: {total_end - total_start:.2f}s")
    return results

import requests
from fastapi import Request, HTTPException
from concurrent.futures import ProcessPoolExecutor
import concurrent.futures
from CreateSection.Functions.process_single_question_wrapper import process_single_question_wrapper

async def process_questions_parallel(openai_model_class, all_questions):
        """Process questions using true parallelism with ThreadPoolExecutor"""
        processed_results = {}
        processed_count = 0
        

       

        # Convert questions dict to list of tuples for processing
        question_items = list(all_questions.items())

        # Create a ThreadPoolExecutor instead of ProcessPoolExecutor
        with concurrent.futures.ThreadPoolExecutor() as executor:
            # Submit all tasks with cached AMI check
            futures = []
            for item in question_items:
                future = executor.submit(
                    process_single_question_wrapper,
                    openai_model_class,
                    item,
                )
                futures.append(future)

            # Process results as they complete
            for future in concurrent.futures.as_completed(futures):
                try:
                    key, result = future.result()
                    processed_results[key] = result
                    processed_count += 1

                   
                        
                except Exception as e:
                    print(f"Error processing future: {str(e)}")

      

       
       
        
        

        return processed_results
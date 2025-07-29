
from Functions.nano_id import *
import random
from Functions.helper import clean_option_text
def generate_bibd_features(total_options: int, features_per_set: int, total_sets: int) -> list:
    """
    Adaptively chooses between BIBD and simple rotation based on parameters.
    """
    try:
        all_sets = []
        options = list(range(1, total_options + 1))
        
        # Determine if we should use simple rotation:
        # 1. When features_per_set <= 2
        # 2. When total_sets is too large relative to possible combinations
        # 3. When total_options is close to features_per_set
        use_simple_rotation = (
            features_per_set <= 2 or 
            total_sets > total_options * 2 or 
            (total_options - features_per_set) <= 1
        )

        if use_simple_rotation:
            # Simple rotation algorithm
            for set_num in range(total_sets):
                start_idx = set_num % total_options
                set_features = []
                for i in range(features_per_set):
                    idx = (start_idx + i) % total_options
                    set_features.append(f"{options[idx]:02d}")
                all_sets.append(set_features)
            return all_sets

        # Full BIBD for more complex cases
        lambda_param = (features_per_set * (features_per_set - 1) * total_sets) // (total_options * (total_options - 1))
        while len(all_sets) < total_sets:
            candidate = []
            available = options.copy()
            
            for _ in range(features_per_set):
                if not available:
                    available = options.copy()
                
                for item in available:
                    test_set = candidate + [item]
                    if is_balanced(test_set, all_sets, lambda_param):
                        candidate.append(item)
                        available.remove(item)
                        break
                        
            if len(candidate) == features_per_set:
                formatted_set = [f"{num:02d}" for num in sorted(candidate)]
                all_sets.append(formatted_set)
                
        return all_sets
    except Exception as e:
        print(f"Algorithm selection error: {str(e)}, falling back to simple rotation")
        # Fallback to simple rotation
        return generate_simple_rotation(total_options, features_per_set, total_sets)

def generate_simple_rotation(total_options: int, features_per_set: int, total_sets: int) -> list:
    """
    Generates a simple rotation design as fallback.
    """
    all_sets = []
    options = list(range(1, total_options + 1))
    
    for set_num in range(total_sets):
        start_idx = set_num % total_options
        set_features = []
        for i in range(features_per_set):
            idx = (start_idx + i) % total_options
            set_features.append(f"{options[idx]:02d}")
        all_sets.append(set_features)
    return all_sets

def is_balanced(candidate, existing_sets, lambda_param):
    """
    Check if adding candidate set maintains balance.
    """
    if not existing_sets:
        return True
        
    # Count pair frequencies
    pair_counts = {}
    for set_features in existing_sets + [candidate]:
        for i in range(len(set_features)):
            for j in range(i + 1, len(set_features)):
                pair = (set_features[i], set_features[j])
                pair_counts[pair] = pair_counts.get(pair, 0) + 1
                
    # Check if any pair exceeds lambda
    return all(count <= lambda_param for count in pair_counts.values())






def generate_random_features(total_options: int, features_per_set: int, total_sets: int) -> list:
    """
    Generate random feature sets with some balance considerations.
    """
    import random
    
    all_sets = []
    options = list(range(1, total_options + 1))
    
    # Keep track of how many times each option appears
    option_counts = {i: 0 for i in options}
    
    print("\nGenerating random feature sets:")
    print(f"Total options: {total_options}")
    print(f"Features per set: {features_per_set}")
    print(f"Total sets needed: {total_sets}")
    
    for set_num in range(total_sets):
        # Prioritize less frequently used options
        available = sorted(options, key=lambda x: (option_counts[x], random.random()))
        # Take the first features_per_set items
        selected = available[:features_per_set]
        # Update counts
        for option in selected:
            option_counts[option] += 1
        # Format and add to sets
        formatted_set = [str(num) for num in sorted(selected)]
        all_sets.append(formatted_set)
        
        print(f"Set {set_num + 1}: {formatted_set} (Original numbers: {selected})")
    
    print("\nFinal option usage counts:")
    print(option_counts)
    
    return all_sets

def generate_bibd_features(total_options: int, features_per_set: int, total_sets: int) -> list:
    """
    Generate Balanced Incomplete Block Design for MaxDiff with formatted labels.
    Limited attempts to avoid infinite loops.
    """
    max_attempts = 1000  # Limit attempts to avoid infinite loops
    all_sets = []
    options = list(range(1, total_options + 1))
    
    lambda_param = (features_per_set * (features_per_set - 1) * total_sets) // (total_options * (total_options - 1))
    
    attempt = 0
    while len(all_sets) < total_sets and attempt < max_attempts:
        candidate = []
        available = options.copy()
        
        for _ in range(features_per_set):
            if not available:
                available = options.copy()
            
            valid_items = [item for item in available 
                         if is_balanced(candidate + [item], all_sets, lambda_param)]
            
            if valid_items:
                item = random.choice(valid_items)
                candidate.append(item)
                available.remove(item)
            else:
                break
        
        if len(candidate) == features_per_set:
            formatted_set = [str(num) for num in sorted(candidate)]
            all_sets.append(formatted_set)
        
        attempt += 1
    
    if len(all_sets) < total_sets:
        raise ValueError("Could not generate BIBD with given parameters")
    
    return all_sets



def process_max_diff_question(question, label, current_time,raw_data):
    base_question = {
        "id": generate_nano_id(),
        "text": question.get("question", ""),
        "type": "maxdiff",
        "label": label,
        "mdText": question.get("question", ""),
        "created": current_time,
        "updated": current_time,
        "skips": [],
        "optout": {"text": None, "allowed": False},
        "dynamic": False,
        "condition": None,
        "confidence": 0.9,
        "issue": None,
        "raw_data":raw_data
    }

    total_sets = question.get("sets", 1)
    features_per_set = question.get("features", 1)
    options_list = question.get("options", [])
    total_options = len(options_list)

    config = {
        "sets": total_sets,
        "designs": 1,
        "features": features_per_set,
        "upperText": question.get("upperText", "Most Important"),
        "lowerText": question.get("lowerText", "Least Important"),
    }

    if options_list:
        if should_use_bibd(total_options, features_per_set, total_sets):
            try:
                all_feature_sets = generate_bibd_features(total_options, features_per_set, total_sets)
            except Exception as e:
                print(f"BIBD generation failed, falling back to random: {str(e)}")
                all_feature_sets = generate_random_features(total_options, features_per_set, total_sets)
        else:
            all_feature_sets = generate_random_features(total_options, features_per_set, total_sets)
            
        design_sets = [{"set": i + 1, "features": feature_set} for i, feature_set in enumerate(all_feature_sets)]
    else:
        design_sets = [{"set": i + 1, "features": ["" for _ in range(features_per_set)]} for i in range(total_sets)]

    config["ranking"] = [{"design": 1, "sets": design_sets}]

    options = []
    if options_list:
        for i, option_dict in enumerate(options_list, start=1):
            option_text = next(iter(option_dict.keys()))
            option = {
                "id": generate_nano_id(),
                "text": clean_option_text(option_text),
                "type": "user",
                # "label": f"{i:02d}",
                "label":str(i),
                "order": i - 1,
                "mdText": clean_option_text(option_text)
            }
            options.append(option)

    base_question["config"] = config
    base_question["options"] = options
    return base_question






def should_use_bibd(total_options: int, features_per_set: int, total_sets: int) -> bool:
    """
    Determine whether to use BIBD or random generation based on parameters.
    """
    # BIBD works well when:
    # 1. total_options is not too large compared to features_per_set
    # 2. The parameters satisfy BIBD requirements
    
    if total_options <= 12 and features_per_set <= 4:
        # Calculate lambda
        lambda_param = (features_per_set * (features_per_set - 1) * total_sets) // (total_options * (total_options - 1))
        # Check if parameters work for BIBD
        if lambda_param > 0 and features_per_set < total_options:
            return True
    return False
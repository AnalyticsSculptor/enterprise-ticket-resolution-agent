import time
from sklearn.metrics import accuracy_score, f1_score, classification_report
from agent import ITSupportAgent

def run_evaluation():
    print("📊 INITIALIZING LLM-AS-A-JUDGE EVALUATION PIPELINE...\n")
    
   
    # We will use 6 highly diverse tickets to test the edge cases of your Agent.
    test_data = [
        {"issue": "My screen went completely black and it smells like burning plastic.", "true_category": "HARDWARE"},
        {"issue": "I need permissions to access the AWS S3 bucket for the marketing team.", "true_category": "ACCESS MANAGEMENT"},
        {"issue": "The company firewall is blocking me from downloading an important PDF.", "true_category": "NETWORK"},
        {"issue": "The main website is returning a 502 Bad Gateway error.", "true_category": "APPLICATION"},
        {"issue": "Someone keeps trying to log into my account from Russia, I keep getting 2FA texts.", "true_category": "SECURITY"},
        {"issue": "The SQL query is taking 45 minutes to execute and locking the tables.", "true_category": "DATABASE"}
    ]

    # 2. Boot up your AI Agent
    agent = ITSupportAgent()
    
    predicted_categories = []
    true_categories = [item["true_category"] for item in test_data]
    escalation_count = 0
    start_time = time.time()

    print("\n🚀 RUNNING TICKETS THROUGH AI AGENT...\n" + "-"*50)
    
    # 3. Process each ticket
    for i, item in enumerate(test_data):
        print(f"Testing Ticket {i+1}/{len(test_data)}...")
        
        # We catch the output of your agent
        decision = agent.process_ticket(item['issue'])
        
        if decision:
            pred_cat = decision['category'].upper()
            predicted_categories.append(pred_cat)
            
            # Track if the AI safely escalated it
            if decision['confidence'] < 0.75:
                escalation_count += 1
        else:
            # Fallback if the JSON parsing failed
            predicted_categories.append("FAILED")
            escalation_count += 1

    # 4. Calculate Business Metrics
    end_time = time.time()
    avg_time = (end_time - start_time) / len(test_data)
    
    accuracy = accuracy_score(true_categories, predicted_categories)
    # Use 'weighted' F1 score to account for multiple categories
    f1 = f1_score(true_categories, predicted_categories, average='weighted', zero_division=0)

    # 5. The Executive Report
    print("\n" + "="*50)
    print("📈 EXECUTIVE EVALUATION REPORT")
    print("="*50)
    print(f"Total Tickets Processed : {len(test_data)}")
    print(f"Average Latency/Ticket  : {avg_time:.2f} seconds")
    print(f"Safe Escalation Rate    : {(escalation_count/len(test_data))*100:.1f}%")
    print("-" * 50)
    print(f"🎯 SYSTEM ACCURACY      : {accuracy * 100:.1f}%")
    print(f"⚖️ SYSTEM F1 SCORE       : {f1:.2f} (1.0 is perfect)")
    print("="*50)

    # Print the detailed breakdown
    print("\n🔍 DETAILED CLASSIFICATION REPORT:")
    print(classification_report(true_categories, predicted_categories, zero_division=0))

if __name__ == "__main__":
    run_evaluation()

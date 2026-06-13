#!/usr/bin/env python3
"""
Generate sample user data for funnel analysis
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

np.random.seed(42)

def generate_sample_data(
    n_users: int = 10000,
    output_path: str = "sample_user_data.csv"
):
    """
    Generate synthetic user journey data
    
    Each user has:
    - signup_date
    - message_sent (whether they sent any message)
    - high_value_action (code execution, file upload, or 5+ turns)
    - repeat_usage (came back within 7 days)
    - sustained_usage (3+ weeks of activity)
    """
    
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 3, 31)
    
    users = []
    
    for i in range(n_users):
        user_id = f"user_{i:05d}"
        signup_date = start_date + timedelta(days=np.random.randint(0, 60))
        
        # Stage 1: First use (80% of users)
        sent_message = np.random.random() < 0.80
        
        if not sent_message:
            users.append({
                'user_id': user_id,
                'signup_date': signup_date,
                'sent_message': False,
                'has_hva': False,
                'repeat_usage': False,
                'sustained_usage': False,
                'churned': True
            })
            continue
        
        # Stage 2: High Value Action (60% of those who used)
        has_hva = np.random.random() < 0.60
        
        # Stage 3: Repeat usage (50% of those with HVA)
        repeat_usage = has_hva and np.random.random() < 0.50
        
        # Stage 4: Sustained usage (40% of those with repeat)
        sustained_usage = repeat_usage and np.random.random() < 0.40
        
        users.append({
            'user_id': user_id,
            'signup_date': signup_date,
            'sent_message': sent_message,
            'has_hva': has_hva,
            'repeat_usage': repeat_usage,
            'sustained_usage': sustained_usage,
            'churned': not sustained_usage
        })
    
    df = pd.DataFrame(users)
    
    # Print summary
    print("=" * 50)
    print("Sample Data Generated")
    print("=" * 50)
    print(f"Total users: {len(df)}")
    print(f"Sent message: {df['sent_message'].sum()}")
    print(f"Has HVA: {df['has_hva'].sum()}")
    print(f"Repeat usage: {df['repeat_usage'].sum()}")
    print(f"Sustained usage: {df['sustained_usage'].sum()}")
    print(f"Churned: {df['churned'].sum()}")
    
    df.to_csv(output_path, index=False)
    print(f"\nSaved to: {output_path}")
    
    return df

if __name__ == "__main__":
    generate_sample_data()

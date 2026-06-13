#!/usr/bin/env python3
"""
Funnel Analysis - Calculate user progression through stages
"""

import pandas as pd
import numpy as np
import json
import os
from datetime import datetime, timedelta

# ============================================================
# 数据生成函数（内置，避免导入问题）
# ============================================================

def generate_sample_data(n_users: int = 10000, output_path: str = "sample_user_data.csv"):
    """
    Generate synthetic user journey data
    """
    np.random.seed(42)
    start_date = datetime(2024, 1, 1)
    
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


# ============================================================
# 数据加载函数
# ============================================================

def load_data(file_path: str = "sample_user_data.csv"):
    """Load user data from CSV"""
    if not os.path.exists(file_path):
        print(f"⚠️ Data file not found: {file_path}")
        print("📊 Generating new sample data...")
        generate_sample_data()
    
    df = pd.read_csv(file_path)
    return df


# ============================================================
# 辅助函数：将 numpy 类型转换为 Python 原生类型
# ============================================================

def convert_to_native(obj):
    """Convert numpy types to Python native types for JSON serialization"""
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, pd.Series):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {k: convert_to_native(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_native(i) for i in obj]
    return obj


# ============================================================
# 漏斗构建函数
# ============================================================

def build_funnel(df):
    """
    Build funnel from user data
    
    Stages:
    - Stage 0: Registered (all users)
    - Stage 1: First Use (sent at least one message)
    - Stage 2: First Value (completed a high-value action)
    - Stage 3: Repeat Usage (came back within 7 days)
    - Stage 4: Sustained Usage (used for 3+ weeks)
    """
    
    total_users = len(df)
    
    # Calculate counts for each stage
    stage_1_users = int(df['sent_message'].sum())
    stage_2_users = int(df['has_hva'].sum())
    stage_3_users = int(df['repeat_usage'].sum())
    stage_4_users = int(df['sustained_usage'].sum())
    
    # Calculate conversion rates
    conv_0_to_1 = stage_1_users / total_users if total_users > 0 else 0
    conv_1_to_2 = stage_2_users / stage_1_users if stage_1_users > 0 else 0
    conv_2_to_3 = stage_3_users / stage_2_users if stage_2_users > 0 else 0
    conv_3_to_4 = stage_4_users / stage_3_users if stage_3_users > 0 else 0
    
    # Calculate dropoff
    dropoff_0 = total_users - stage_1_users
    dropoff_1 = stage_1_users - stage_2_users
    dropoff_2 = stage_2_users - stage_3_users
    dropoff_3 = stage_3_users - stage_4_users
    
    # Build funnel data structure
    funnel = [
        {
            'stage': 'Registered',
            'stage_id': 0,
            'users': int(total_users),
            'conversion_from_previous': 1.0,
            'dropoff': 0.0,
            'dropoff_users': 0,
            'overall_conversion': 1.0
        },
        {
            'stage': 'First Use',
            'stage_id': 1,
            'users': stage_1_users,
            'conversion_from_previous': round(conv_0_to_1, 4),
            'dropoff': round(1 - conv_0_to_1, 4),
            'dropoff_users': dropoff_0,
            'overall_conversion': round(stage_1_users / total_users, 4)
        },
        {
            'stage': 'First Value (HVA)',
            'stage_id': 2,
            'users': stage_2_users,
            'conversion_from_previous': round(conv_1_to_2, 4),
            'dropoff': round(1 - conv_1_to_2, 4),
            'dropoff_users': dropoff_1,
            'overall_conversion': round(stage_2_users / total_users, 4)
        },
        {
            'stage': 'Repeat Usage',
            'stage_id': 3,
            'users': stage_3_users,
            'conversion_from_previous': round(conv_2_to_3, 4),
            'dropoff': round(1 - conv_2_to_3, 4),
            'dropoff_users': dropoff_2,
            'overall_conversion': round(stage_3_users / total_users, 4)
        },
        {
            'stage': 'Sustained Usage',
            'stage_id': 4,
            'users': stage_4_users,
            'conversion_from_previous': round(conv_3_to_4, 4),
            'dropoff': round(1 - conv_3_to_4, 4),
            'dropoff_users': dropoff_3,
            'overall_conversion': round(stage_4_users / total_users, 4)
        }
    ]
    
    return funnel, total_users


# ============================================================
# HTML 报告生成函数
# ============================================================

def generate_html_report(funnel, total_users, output_path="output/report.html"):
    """Generate HTML report"""
    
    # Prepare data for JavaScript chart (convert to Python native types)
    stages = [s['stage'] for s in funnel]
    users = [int(s['users']) for s in funnel]
    dropoff_rates = [float(s['dropoff'] * 100) for s in funnel]
    
    # Find bottlenecks (stages with >30% dropoff)
    bottlenecks = []
    for s in funnel:
        if s['dropoff'] > 0.30 and s['stage_id'] > 0:
            bottlenecks.append({
                'stage': s['stage'],
                'dropoff_rate': f"{s['dropoff']*100:.1f}%",
                'users_lost': f"{s['dropoff_users']:,}"
            })
    
    # Generate bottlenecks HTML
    bottlenecks_html = ""
    if bottlenecks:
        bottlenecks_html = '<div class="bottlenecks-list">'
        for b in bottlenecks:
            bottlenecks_html += f'''
            <div class="bottleneck-item">
                <span class="bottleneck-stage">{b['stage']}</span>
                <span class="bottleneck-rate">{b['dropoff_rate']}</span>
                <span class="bottleneck-users">{b['users_lost']} users lost</span>
            </div>
            '''
        bottlenecks_html += '</div>'
    else:
        bottlenecks_html = '<p class="no-bottlenecks">✅ No major bottlenecks detected (dropoff >30%)</p>'
    
    # Generate funnel table HTML
    table_rows = ""
    for s in funnel:
        if s['stage_id'] == 0:
            continue
        warning_class = 'warning' if s['dropoff'] > 0.30 else ''
        table_rows += f'''
        <tr>
            <td>{s['stage']}</td>
            <td>{s['users']:,}</td>
            <td>{s['overall_conversion']*100:.1f}%</td>
            <td>{s['conversion_from_previous']*100:.1f}%</td>
            <td class="{warning_class}">{s['dropoff']*100:.1f}%</td>
            <td>{s['dropoff_users']:,}</td>
        </tr>
        '''
    
    # Calculate sustained users and retention
    sustained_users = funnel[-1]['users']
    overall_retention = funnel[-1]['overall_conversion'] * 100
    
    # Prepare JSON data (ensure it's JSON serializable)
    funnel_json_data = {
        'stages': stages,
        'users': users,
        'dropoff_rates': dropoff_rates
    }
    funnel_json_str = json.dumps(funnel_json_data)
    
    # HTML Template
    html_template = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Funnel Analysis Report | Skill 1.2B-1</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 40px 20px;
        }
        .container { max-width: 1200px; margin: 0 auto; }
        .header {
            background: white;
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 30px;
            text-align: center;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        .header h1 { color: #667eea; font-size: 1.8rem; margin-bottom: 10px; }
        .header .subtitle { color: #666; margin-bottom: 20px; }
        .stats-grid {
            display: flex;
            justify-content: center;
            gap: 30px;
            margin-top: 20px;
            flex-wrap: wrap;
        }
        .stat-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px 30px;
            border-radius: 16px;
            text-align: center;
            min-width: 150px;
        }
        .stat-card .label { font-size: 0.8rem; opacity: 0.9; margin-bottom: 5px; }
        .stat-card .value { font-size: 2rem; font-weight: bold; }
        .section {
            background: white;
            border-radius: 20px;
            padding: 25px;
            margin-bottom: 30px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.08);
        }
        .section h2 {
            color: #333;
            font-size: 1.3rem;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #667eea;
        }
        .chart-container { max-width: 600px; margin: 20px auto; position: relative; }
        canvas { max-height: 400px; }
        .table-wrapper { overflow-x: auto; }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 12px 15px; text-align: center; border-bottom: 1px solid #eee; }
        th { background: #f8f9fa; font-weight: 600; color: #667eea; }
        tr:hover td { background: #f5f5f5; }
        .warning { color: #e74c3c; font-weight: bold; }
        .bottlenecks-list { display: flex; flex-direction: column; gap: 12px; }
        .bottleneck-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px;
            background: #fee2e2;
            border-radius: 12px;
            border-left: 4px solid #e74c3c;
        }
        .bottleneck-stage { font-weight: 600; color: #c0392b; }
        .bottleneck-rate { font-size: 1.2rem; font-weight: bold; color: #e74c3c; }
        .bottleneck-users { color: #666; }
        .no-bottlenecks { text-align: center; padding: 30px; background: #d5f5e3; border-radius: 12px; color: #27ae60; }
        .footer { text-align: center; padding: 20px; color: rgba(255,255,255,0.7); font-size: 0.8rem; }
        @media (max-width: 768px) {
            .stats-grid { gap: 15px; }
            .stat-card { padding: 12px 20px; }
            .stat-card .value { font-size: 1.3rem; }
            th, td { padding: 8px 10px; font-size: 0.8rem; }
        }
    </style>
</head>
<body>
<div class="container">
    <div class="header">
        <h1>📊 User Funnel Analysis</h1>
        <div class="subtitle">Stage Definition & Conversion Rate Calculation</div>
        <div class="stats-grid">
            <div class="stat-card">
                <div class="label">Total Users</div>
                <div class="value">{{TOTAL_USERS}}</div>
            </div>
            <div class="stat-card">
                <div class="label">Sustained Users</div>
                <div class="value">{{SUSTAINED_USERS}}</div>
            </div>
            <div class="stat-card">
                <div class="label">Overall Retention</div>
                <div class="value">{{OVERALL_RETENTION}}%</div>
            </div>
        </div>
    </div>
    
    <div class="section">
        <h2>📈 Funnel Visualization</h2>
        <div class="chart-container">
            <canvas id="funnelChart"></canvas>
        </div>
    </div>
    
    <div class="section">
        <h2>⚠️ Bottlenecks (Dropoff > 30%)</h2>
        {{BOTTLENECKS}}
    </div>
    
    <div class="section">
        <h2>📋 Funnel Details</h2>
        <div class="table-wrapper">
            <table>
                <thead>
                    <tr>
                        <th>Stage</th>
                        <th>Users</th>
                        <th>Overall Conversion</th>
                        <th>Conversion from Previous</th>
                        <th>Dropoff Rate</th>
                        <th>Users Lost</th>
                    </tr>
                </thead>
                <tbody>
                    {{FUNNEL_TABLE_ROWS}}
                </tbody>
            </table>
        </div>
    </div>
    
    <div class="footer">
        <p>Generated by Skill 1.2B-1: Funnel Stage Definition & Conversion Analysis</p>
        <p>Stages: Registered → First Use → First Value (HVA) → Repeat Usage → Sustained Usage</p>
    </div>
</div>

<script>
    const funnelData = {{FUNNEL_DATA}};
    const ctx = document.getElementById('funnelChart').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: funnelData.stages,
            datasets: [
                {
                    label: 'Users',
                    data: funnelData.users,
                    backgroundColor: 'rgba(102, 126, 234, 0.7)',
                    borderColor: 'rgba(102, 126, 234, 1)',
                    borderWidth: 1,
                    borderRadius: 8,
                    yAxisID: 'y'
                },
                {
                    label: 'Dropoff Rate (%)',
                    data: funnelData.dropoff_rates,
                    type: 'line',
                    borderColor: '#e74c3c',
                    backgroundColor: 'rgba(231, 76, 60, 0.1)',
                    borderWidth: 2,
                    fill: false,
                    tension: 0.3,
                    pointRadius: 5,
                    pointBackgroundColor: '#e74c3c',
                    yAxisID: 'y1'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: { position: 'top' },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            let label = context.dataset.label || '';
                            let value = context.raw;
                            if (context.dataset.label === 'Users') {
                                return label + ': ' + value.toLocaleString();
                            }
                            return label + ': ' + value.toFixed(1) + '%';
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: { display: true, text: 'Number of Users' },
                    ticks: { callback: function(value) { return value.toLocaleString(); } }
                },
                y1: {
                    position: 'right',
                    beginAtZero: true,
                    max: 100,
                    title: { display: true, text: 'Dropoff Rate (%)' },
                    ticks: { callback: function(value) { return value + '%'; } }
                }
            }
        }
    });
</script>
</body>
</html>'''
    
    # Replace placeholders
    html = html_template
    html = html.replace('{{TOTAL_USERS}}', f"{total_users:,}")
    html = html.replace('{{SUSTAINED_USERS}}', f"{sustained_users:,}")
    html = html.replace('{{OVERALL_RETENTION}}', f"{overall_retention:.1f}")
    html = html.replace('{{BOTTLENECKS}}', bottlenecks_html)
    html = html.replace('{{FUNNEL_TABLE_ROWS}}', table_rows)
    html = html.replace('{{FUNNEL_DATA}}', funnel_json_str)
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"\n✅ Report saved to: {output_path}")
    return output_path


# ============================================================
# 主函数
# ============================================================

def main():
    print("=" * 60)
    print("Skill 1.2B-1: Funnel Stage Definition & Conversion Analysis")
    print("=" * 60)
    
    # Load data (will generate if not exists)
    print("\n📂 Loading user data...")
    df = load_data()
    print(f"   Total users: {len(df)}")
    
    # Build funnel
    print("\n📊 Building funnel...")
    funnel, total_users = build_funnel(df)
    
    # Print results to console
    print("\n" + "-" * 60)
    print("USER FUNNEL")
    print("-" * 60)
    for s in funnel:
        if s['stage_id'] == 0:
            print(f"{s['stage']:25} {s['users']:>8,} (starting point)")
        else:
            print(f"{s['stage']:25} {s['users']:>8,} ({s['overall_conversion']*100:>5.1f}% overall, {s['conversion_from_previous']*100:>5.1f}% from previous)")
    
    # Print dropoff analysis
    print("\n" + "-" * 60)
    print("DROPOFF ANALYSIS")
    print("-" * 60)
    for s in funnel:
        if s['stage_id'] > 0:
            warning = "⚠️ BOTTLENECK" if s['dropoff'] > 0.30 else ""
            print(f"  {s['stage']}: {s['dropoff']*100:.1f}% dropoff ({s['dropoff_users']:,} users) {warning}")
    
    # Generate HTML report
    print("\n📄 Generating HTML report...")
    report_path = generate_html_report(funnel, total_users)
    
    print("\n" + "=" * 60)
    print("✅ ANALYSIS COMPLETE!")
    print("=" * 60)
    print(f"\n📁 Open report: {report_path}")


if __name__ == "__main__":
    main()

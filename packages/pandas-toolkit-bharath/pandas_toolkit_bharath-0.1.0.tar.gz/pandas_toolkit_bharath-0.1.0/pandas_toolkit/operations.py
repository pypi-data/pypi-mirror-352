def display_head_tail(df):
    choice = input("Display (1) Top 5 rows or (2) Bottom 5 rows? Enter 1 or 2: ").strip()
    if choice == '1':
        print("\n--- Top 5 rows ---")
        print(df.head(5))
    elif choice == '2':
        print("\n--- Bottom 5 rows ---")
        print(df.tail(5))
    else:
        print("Invalid choice. Showing top 5 rows by default.")
        print(df.head(5))

def filter_data(df):
    print("\nYou can filter data by entering a pandas query expression.")
    print("Example: Age > 30 and Gender == 'Male'")
    print("Available columns:", list(df.columns))
    
    condition = input("Enter your filter condition (leave empty to skip filtering): ").strip()
    if not condition:
        print("No filter applied.")
        return df

    try:
        filtered_df = df.query(condition)
        print(f"\nFiltered data: {len(filtered_df)} rows matched.")
        display_head_tail(filtered_df)
        return filtered_df
    except Exception as e:
        print(f"Invalid filter condition: {e}")
        print("Returning original dataframe.")
        return df

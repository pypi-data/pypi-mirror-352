


def generate_ouput(df):
    if not df.empty:
        df.to_csv("synthetic_data.csv", index=False)
        print("✅ Synthetic data saved to synthetic_data.csv")
    else:
        print("❌ No valid data to save.")
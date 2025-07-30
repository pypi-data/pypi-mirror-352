def show_summary(df):
    print("\n--- Data Summary (describe) ---")
    print(df.describe(include='all'))

def show_info(df):
    print("\n--- Data Info ---")
    buffer = []
    df.info(buf=buffer)
    # Since df.info prints to stdout, capture it using StringIO alternative:
    import io
    buf = io.StringIO()
    df.info(buf=buf)
    info = buf.getvalue()
    print(info)
